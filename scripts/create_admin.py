#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_connection, init_db
from backend.utils.security import hash_password
import uuid

def create_admin():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    username = "admin"
    password = "admin123"
    hashed = hash_password(password)
    tenant_id = str(uuid.uuid4())
    role_id = 1

    try:
        cursor.execute(
            "INSERT INTO users (username, password, tenant_id, role_id) VALUES (?, ?, ?, ?)",
            (username, hashed, tenant_id, role_id)
        )
        conn.commit()
        print(f"✅ Admin created: {username} / {password}")
        print(f"✅ Tenant ID: {tenant_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_admin()