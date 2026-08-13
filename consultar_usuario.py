import json
import sqlite3
from pathlib import Path

db = Path(__file__).parent / "finanzas.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

print("=== Archivo de base de datos ===")
print(db.resolve())
print()

print("=== Usuarios registrados ===")
for u in conn.execute("SELECT id, username, created_at FROM users"):
    print(dict(u))
print()

username = "RicardoDiazCampos"
row = conn.execute(
    """
    SELECT u.id, u.username, u.created_at, p.updated_at, p.profile_json
    FROM users u
    JOIN user_profiles p ON u.id = p.user_id
    WHERE u.username = ?
    """,
    (username,),
).fetchone()

if not row:
    print(f"No se encontro el usuario '{username}'")
    conn.close()
    raise SystemExit(1)

data = dict(row)
profile = json.loads(data.pop("profile_json"))

print(f"=== Datos de {username} ===")
print(f"ID usuario: {data['id']}")
print(f"Creado: {data['created_at']}")
print(f"Ultima actualizacion perfil: {data['updated_at']}")
print()
print("=== Perfil financiero (JSON guardado) ===")
print(json.dumps(profile, indent=2, ensure_ascii=False))
print()

from models import FinancialProfile
from serialization import profile_from_dict

p = profile_from_dict(profile)
print("=== Resumen calculado ===")
for label, value in p.summary_lines():
    safe = label.replace("\u2212", "-")
    print(f"  {safe:32} {value:,.2f}")

conn.close()
