"""
Wrapper sobre el SDK google-genai para el chat inteligente web.

Cascada de modelos: intenta en orden desde el más barato al más capaz.
Cuando un modelo devuelve 429 (quota), escala al siguiente automáticamente.
Si todos fallan, lanza AllModelsExhaustedError para que el router derive a email.
"""

import logging

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.chat_context import build_system_prompt

logger = logging.getLogger(__name__)

# Contadores acumulados en la vida del proceso (se reinician al reiniciar).
_model_request_count: dict[str, int] = {}
_model_token_count: dict[str, int] = {}
_model_quota_hit: set[str] = set()  # modelos que ya dieron 429

# Límites conservadores (80% del free tier conocido) para escalar preventivamente.
# RPD = requests/day  |  TPD = tokens/day
_FREE_TIER_SAFE_LIMIT: dict[str, int] = {
    "gemini-2.0-flash-lite": 1200,   # free tier: ~1500 RPD
    "gemini-2.0-flash":      1200,   # free tier: ~1500 RPD
    "gemini-2.5-flash":      16,     # free tier: 20 RPD
}
_FREE_TIER_TOKEN_LIMIT: dict[str, int] = {
    "gemini-2.0-flash-lite": 800_000,   # free tier: ~1 M TPD
    "gemini-2.0-flash":      800_000,
    "gemini-2.5-flash":      200_000,   # free tier: ~250 K TPD
}
_DEFAULT_SAFE_LIMIT = 800
_DEFAULT_TOKEN_LIMIT = 600_000


class AllModelsExhaustedError(Exception):
    """Todos los modelos de la cascada alcanzaron su cuota."""


def _client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def _should_skip(model: str) -> bool:
    """True si el modelo ya dio 429 o está cerca del límite seguro (RPD o TPD)."""
    if model in _model_quota_hit:
        return True
    req_limit = _FREE_TIER_SAFE_LIMIT.get(model, _DEFAULT_SAFE_LIMIT)
    if _model_request_count.get(model, 0) >= req_limit:
        return True
    tok_limit = _FREE_TIER_TOKEN_LIMIT.get(model, _DEFAULT_TOKEN_LIMIT)
    return _model_token_count.get(model, 0) >= tok_limit


def _register_use(model: str, tokens: int = 0) -> None:
    _model_request_count[model] = _model_request_count.get(model, 0) + 1
    if tokens:
        _model_token_count[model] = _model_token_count.get(model, 0) + tokens


def _is_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "429" in msg or "resource_exhausted" in msg or "quota" in msg


def _build_contents(history: list[dict], message: str) -> list:
    max_turns = settings.chat_max_turns * 2
    trimmed = history[-max_turns:] if len(history) > max_turns else history
    contents = []
    for turn in trimmed:
        role = "user" if turn.get("role") == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part(text=turn.get("text", ""))])
        )
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
    return contents


def send_chat(history: list[dict], message: str) -> str:
    """
    Envía un mensaje a Gemini recorriendo la cascada de modelos.
    history: [{"role": "user"|"model", "text": "..."}]
    message: nuevo mensaje del usuario.
    Retorna: texto de la respuesta.
    Lanza AllModelsExhaustedError si todos los modelos están en cuota.
    """
    client = _client()
    system_prompt = build_system_prompt()
    contents = _build_contents(history, message)

    base_config = dict(
        system_instruction=system_prompt,
        max_output_tokens=1024,
        temperature=0.7,
    )

    cascade = settings.chat_model_cascade
    last_error = None

    for model in cascade:
        if _should_skip(model):
            logger.info(f"Chat: saltando '{model}' (cuota proyectada agotada)")
            continue

        # Intentar con Google Search, fallback sin él si el modelo no lo soporta
        for use_search in (True, False):
            try:
                cfg = types.GenerateContentConfig(
                    **base_config,
                    **({"tools": [types.Tool(google_search=types.GoogleSearch())]} if use_search else {}),
                )
                response = client.models.generate_content(
                    model=model, contents=contents, config=cfg
                )
                tokens = getattr(getattr(response, "usage_metadata", None), "total_token_count", 0) or 0
                _register_use(model, tokens)
                if model != cascade[0]:
                    logger.info(f"Chat: usando modelo de cascada '{model}' ({tokens} tokens acumulados: {_model_token_count.get(model, 0)})")
                return response.text or ""
            except Exception as e:
                if _is_quota_error(e):
                    last_error = e
                    _model_quota_hit.add(model)
                    logger.warning(f"Chat: cuota agotada en '{model}', escalando...")
                    break  # saltar al siguiente modelo
                if use_search:
                    continue  # reintentar sin search
                last_error = e
                logger.warning(f"Chat: error en '{model}': {e}")
                break  # saltar al siguiente modelo

    raise AllModelsExhaustedError(
        f"Todos los modelos de la cascada están sin cuota disponible. Último error: {last_error}"
    )
