"""Persistencia en SQLite: usuarios y perfiles financieros."""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

from models import FinancialProfile
from serialization import profile_from_dict, profile_to_dict


def get_db_path() -> Path:
    """Ruta de la base de datos según entorno (local vs Netlify Functions)."""
    configured = os.environ.get("DATABASE_PATH")
    if configured:
        return Path(configured)
    if os.environ.get("NETLIFY") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return Path("/tmp/finanzas.db")
    return Path(__file__).parent / "finanzas.db"


DB_PATH = get_db_path()


def _connect() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                profile_json TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )


def validar_usuario_unico(usuario: str) -> bool:
    """True si el nombre de usuario está disponible."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (usuario,),
        ).fetchone()
    return row is None


def crear_usuario(usuario: str, password_hash: str) -> int:
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (usuario, password_hash),
        )
        user_id = int(cursor.lastrowid)
        empty = profile_to_dict(FinancialProfile())
        conn.execute(
            "INSERT INTO user_profiles (user_id, profile_json) VALUES (?, ?)",
            (user_id, json.dumps(empty)),
        )
    return user_id


def obtener_usuario_por_nombre(usuario: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (usuario,),
        ).fetchone()
    return dict(row) if row else None


def obtener_usuario_por_id(user_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def cargar_datos_usuario(user_id: int) -> FinancialProfile:
    with _connect() as conn:
        row = conn.execute(
            "SELECT profile_json FROM user_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    if not row:
        return FinancialProfile()
    return profile_from_dict(json.loads(row["profile_json"]))


def guardar_datos_usuario(user_id: int, profile: FinancialProfile) -> None:
    payload = json.dumps(profile_to_dict(profile))
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO user_profiles (user_id, profile_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                profile_json = excluded.profile_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, payload),
        )


def reiniciar_datos_usuario(user_id: int) -> None:
    guardar_datos_usuario(user_id, FinancialProfile())
