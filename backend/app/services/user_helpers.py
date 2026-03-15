"""
Helpers compartidos para routers de usuarios y clientes.

Estas funciones estaban duplicadas en user.py y client.py.
Se extraen aquí para un único punto de verdad.
"""


def split_full_name(full_name: str) -> tuple[str | None, str | None]:
    """Descompone un nombre completo en first_name y last_name."""
    parts = (full_name or "").strip().split()
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], " ".join(parts[1:])
