"""
Wrapper sobre el SDK google-genai para el chat inteligente web.
Maneja historial stateless: cada request reconstruye el contexto completo.
"""

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.chat_context import build_system_prompt


def _client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def send_chat(history: list[dict], message: str) -> str:
    """
    Envía un mensaje a Gemini con historial previo como contexto.

    history: lista de dicts [{"role": "user"|"model", "text": "..."}]
             se trunca a los últimos chat_max_turns * 2 turnos.
    message: texto nuevo del usuario.
    Retorna: texto de la respuesta del modelo.
    """
    client = _client()
    system_prompt = build_system_prompt()

    max_turns = settings.chat_max_turns * 2
    trimmed_history = history[-max_turns:] if len(history) > max_turns else history

    contents = []
    for turn in trimmed_history:
        role = "user" if turn.get("role") == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part(text=turn.get("text", ""))])
        )
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=1024,
            temperature=0.7,
        ),
    )
    return response.text or ""
