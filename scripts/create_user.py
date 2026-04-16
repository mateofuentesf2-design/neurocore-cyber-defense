import sys
import os

# ✅ Agregar raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.utils.security import hash_password
from backend.db import get_connection

def create_user():
    conn = get_connection()
    cursor = conn.cursor()

    username = "mateofuentesf2"
    password = "123Maogig*"
    tenant_id = "company_a"

    hashed = hash_password(password)

    cursor.execute(
        "INSERT INTO users (username, password, tenant_id) VALUES (%s, %s, %s)",
        (username, hashed, tenant_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Usuario creado correctamente")

if __name__ == "__main__":
    create_user()