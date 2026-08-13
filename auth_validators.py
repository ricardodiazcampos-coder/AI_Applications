"""Validación de contraseñas y nombres de usuario."""

import re
from typing import Optional, Tuple


def validar_contrasena(contrasena: str) -> Tuple[bool, Optional[str]]:
    """
    Reglas del laboratorio:
    - Mínimo 5 caracteres.
    - Al menos un carácter especial.
    """
    if len(contrasena) < 5:
        return False, "La contraseña debe tener al menos 5 caracteres."
    if not re.search(r"[^\w\s]", contrasena):
        return False, "La contraseña debe incluir al menos un carácter especial."
    return True, None


def validar_nombre_usuario(usuario: str) -> Tuple[Optional[str], Optional[str]]:
    text = usuario.strip()
    if not text:
        return None, "El nombre de usuario es obligatorio."
    if len(text) < 3:
        return None, "El nombre de usuario debe tener al menos 3 caracteres."
    if not re.match(r"^[a-zA-Z0-9_.-]+$", text):
        return None, "Use solo letras, números, punto, guion o guion bajo."
    return text, None
