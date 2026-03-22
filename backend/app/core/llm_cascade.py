"""
Cascada multi-proveedor para el chat inteligente.

Orden de intento: más barato / más cuota → más capaz / menos cuota.
Cada entrada de la cascada tiene el formato "proveedor:modelo".
Si el proveedor no tiene API key configurada se salta sin error.
Si todos los modelos/proveedores se agotan → AllModelsExhaustedError → handoff email.

Proveedores soportados (todos con free tier):
  gemini   — Google Gemini (google-genai SDK)
  groq     — Groq (API compatible OpenAI, httpx)
  mistral  — Mistral AI (API compatible OpenAI, httpx)
"""

import logging

import httpx
from google import genai
from google.genai import types

from app.core.config import settings
from app.core.chat_context import build_system_prompt

logger = logging.getLogger(__name__)

# ── Contadores en memoria (se reinician al reiniciar el proceso) ──────────────
_req_count: dict[str, int] = {}
_tok_count: dict[str, int] = {}
_quota_hit: set[str] = set()

# ── Límites conservadores (80% del free tier conocido) ───────────────────────
# Formato clave: "proveedor:modelo"
# Valor: (RPD_safe, TPD_safe)  — 0 = no aplicar ese límite
_SAFE: dict[str, tuple[int, int]] = {
    "gemini:gemini-2.0-flash-lite": (1200, 800_000),
    "gemini:gemini-2.0-flash":      (1200, 800_000),
    "gemini:gemini-2.5-flash":      (16,   200_000),
    "groq:llama-3.1-8b-instant":    (14_000, 0),   # free tier ~14400 RPD
    "groq:llama-3.3-70b-versatile": (800,    0),   # free tier ~1000 RPD
    "groq:gemma2-9b-it":            (14_000, 0),
    "groq:mixtral-8x7b-32768":      (14_000, 0),
    "mistral:mistral-small-latest": (400,    0),   # free tier estimado
    "mistral:open-mistral-7b":      (400,    0),
}
_DEFAULT_RPD = 800
_DEFAULT_TPD = 600_000


class AllModelsExhaustedError(Exception):
    """Todos los modelos de la cascada alcanzaron su cuota."""


def _key(provider: str, model: str) -> str:
    return f"{provider}:{model}"


def _should_skip(provider: str, model: str) -> bool:
    k = _key(provider, model)
    if k in _quota_hit:
        return True
    rpd_limit, tpd_limit = _SAFE.get(k, (_DEFAULT_RPD, _DEFAULT_TPD))
    if rpd_limit and _req_count.get(k, 0) >= rpd_limit:
        return True
    if tpd_limit and _tok_count.get(k, 0) >= tpd_limit:
        return True
    return False


def _register_use(provider: str, model: str, tokens: int = 0) -> None:
    k = _key(provider, model)
    _req_count[k] = _req_count.get(k, 0) + 1
    if tokens:
        _tok_count[k] = _tok_count.get(k, 0) + tokens


def _is_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return (
        "429" in msg
        or "resource_exhausted" in msg
        or "quota" in msg
        or "rate_limit" in msg
        or "rate limit" in msg
        or "too many requests" in msg
    )


# ── Conversión de historial ───────────────────────────────────────────────────

def _trim_history(history: list[dict]) -> list[dict]:
    max_turns = settings.chat_max_turns * 2
    return history[-max_turns:] if len(history) > max_turns else history


# ── Proveedor: Gemini ─────────────────────────────────────────────────────────

def _send_gemini(model: str, system_prompt: str, history: list[dict], message: str) -> tuple[str, int]:
    client = genai.Client(api_key=settings.gemini_api_key)
    contents = []
    for turn in _trim_history(history):
        role = "user" if turn.get("role") == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=turn.get("text", ""))]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    base_cfg = dict(system_instruction=system_prompt, max_output_tokens=1024, temperature=0.7)

    for use_search in (True, False):
        try:
            cfg = types.GenerateContentConfig(
                **base_cfg,
                **({"tools": [types.Tool(google_search=types.GoogleSearch())]} if use_search else {}),
            )
            r = client.models.generate_content(model=model, contents=contents, config=cfg)
            tokens = getattr(getattr(r, "usage_metadata", None), "total_token_count", 0) or 0
            return r.text or "", tokens
        except Exception as e:
            if _is_quota_error(e):
                raise
            if use_search:
                continue   # reintentar sin search
            raise


# ── Proveedor: compatible OpenAI (Groq, Mistral) ─────────────────────────────

def _send_openai_compat(
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    history: list[dict],
    message: str,
) -> tuple[str, int]:
    messages = [{"role": "system", "content": system_prompt}]
    for turn in _trim_history(history):
        role = "user" if turn.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": turn.get("text", "")})
    messages.append({"role": "user", "content": message})

    with httpx.Client(timeout=30) as client:
        r = client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "max_tokens": 1024, "temperature": 0.7},
        )
    if r.status_code == 429:
        raise Exception(f"429 rate_limit {base_url}: {r.text[:200]}")
    r.raise_for_status()
    data = r.json()
    text = data["choices"][0]["message"]["content"] or ""
    tokens = data.get("usage", {}).get("total_tokens", 0)
    return text, tokens


# ── Dispatcher ────────────────────────────────────────────────────────────────

def _dispatch(
    provider: str,
    model: str,
    system_prompt: str,
    history: list[dict],
    message: str,
) -> tuple[str, int]:
    if provider == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY no configurada")
        return _send_gemini(model, system_prompt, history, message)

    elif provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY no configurada")
        return _send_openai_compat(
            "https://api.groq.com/openai/v1",
            settings.groq_api_key,
            model, system_prompt, history, message,
        )

    elif provider == "mistral":
        if not settings.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY no configurada")
        return _send_openai_compat(
            "https://api.mistral.ai/v1",
            settings.mistral_api_key,
            model, system_prompt, history, message,
        )

    else:
        raise ValueError(f"Proveedor desconocido: '{provider}'")


# ── Cascada principal ─────────────────────────────────────────────────────────

def send_chat(history: list[dict], message: str) -> str:
    """
    Envía un mensaje recorriendo la cascada multi-proveedor.
    history: [{"role": "user"|"model", "text": "..."}]
    Retorna texto de la respuesta.
    Lanza AllModelsExhaustedError si todos los modelos están en cuota.
    """
    system_prompt = build_system_prompt()
    cascade = settings.chat_model_cascade   # list of "provider:model" strings
    last_error = None

    for entry in cascade:
        if ":" not in entry:
            logger.warning(f"Cascade entry inválida (sin proveedor): '{entry}', saltando")
            continue

        provider, model = entry.split(":", 1)

        if _should_skip(provider, model):
            logger.info(f"Chat: saltando '{entry}' (cuota proyectada agotada)")
            continue

        try:
            text, tokens = _dispatch(provider, model, system_prompt, history, message)
            _register_use(provider, model, tokens)
            if entry != cascade[0]:
                total = _tok_count.get(_key(provider, model), 0)
                logger.info(f"Chat: respondió '{entry}' ({tokens} tokens, acum {total})")
            return text

        except Exception as e:
            if isinstance(e, ValueError):
                # API key no configurada — saltar sin marcar como quota hit
                logger.debug(f"Chat: saltando '{entry}' ({e})")
                last_error = e
            elif _is_quota_error(e):
                _quota_hit.add(_key(provider, model))
                logger.warning(f"Chat: cuota agotada en '{entry}', escalando...")
                last_error = e
            else:
                logger.warning(f"Chat: error en '{entry}': {e}")
                last_error = e

    raise AllModelsExhaustedError(
        f"Todos los modelos de la cascada están sin cuota disponible. Último error: {last_error}"
    )


def query_json(user_prompt: str, system_prompt: str) -> dict:
    """
    Consulta puntual a la cascada esperando respuesta JSON.
    Sin historial de chat. Retorna dict parseado.
    Lanza AllModelsExhaustedError si todos los modelos están agotados.
    """
    import json
    import re

    cascade = settings.chat_model_cascade
    last_error = None

    for entry in cascade:
        if ":" not in entry:
            continue
        provider, model = entry.split(":", 1)
        if _should_skip(provider, model):
            continue
        try:
            text, tokens = _dispatch(provider, model, system_prompt, [], user_prompt)
            _register_use(provider, model, tokens)
            # Extraer JSON del texto (puede venir entre ```json ... ``` o solo {})
            match = re.search(r'\{.*\}', text, re.DOTALL)
            raw = match.group() if match else text.strip()
            return json.loads(raw)
        except json.JSONDecodeError as e:
            last_error = ValueError(f"Respuesta no es JSON válido de '{entry}': {e}")
            continue
        except Exception as e:
            if isinstance(e, ValueError):
                last_error = e
            elif _is_quota_error(e):
                _quota_hit.add(_key(provider, model))
                logger.warning(f"query_json: cuota agotada en '{entry}', escalando...")
                last_error = e
            else:
                logger.warning(f"query_json: error en '{entry}': {e}")
                last_error = e

    raise AllModelsExhaustedError(
        f"query_json: todos los modelos agotados. Último error: {last_error}"
    )
