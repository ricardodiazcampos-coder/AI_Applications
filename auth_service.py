"""Lógica de autenticación (separada de la lógica financiera)."""

from typing import Optional, Tuple

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from auth_validators import validar_contrasena, validar_nombre_usuario
from persistence import (
    crear_usuario,
    obtener_usuario_por_id,
    obtener_usuario_por_nombre,
    validar_usuario_unico,
)


class User(UserMixin):
    def __init__(self, user_id: int, username: str) -> None:
        self.id = user_id
        self.username = username


def get_user_by_id(user_id: int) -> Optional[User]:
    row = obtener_usuario_por_id(user_id)
    if not row:
        return None
    return User(row["id"], row["username"])


def registrar_usuario(usuario: str, contrasena: str) -> Tuple[bool, Optional[str]]:
    username, err = validar_nombre_usuario(usuario)
    if err:
        return False, err

    ok, pwd_err = validar_contrasena(contrasena)
    if not ok:
        return False, pwd_err

    if not validar_usuario_unico(username):
        return False, "Ese nombre de usuario ya existe."

    password_hash = generate_password_hash(contrasena)
    crear_usuario(username, password_hash)
    return True, None


def iniciar_sesion(usuario: str, contrasena: str) -> Tuple[Optional[User], Optional[str]]:
    username, err = validar_nombre_usuario(usuario)
    if err:
        return None, err

    row = obtener_usuario_por_nombre(username)
    if not row or not check_password_hash(row["password_hash"], contrasena):
        return None, "Usuario o contraseña incorrectos."

    return User(row["id"], row["username"]), None
