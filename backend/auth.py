from fastapi import Header, HTTPException, Depends
from backend.db import get_connection

# ==============================
# 🔐 API KEY VALIDATION
# ==============================

def validate_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key missing")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT tenant_id FROM api_keys WHERE key=%s",
        (x_api_key,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return result[0]


# ==============================
# 🔐 RBAC PERMISSION CHECK
# ==============================

def require_permission(permission_name: str):
    def permission_checker(user=Depends(verify_token)):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            JOIN role_permissions rp ON rp.role_id = r.id
            JOIN permissions p ON rp.permission_id = p.id
            WHERE u.id = %s
        """, (user["user_id"],))

        permissions = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        if permission_name not in permissions:
            raise HTTPException(status_code=403, detail="Permission denied")

        return user

    return permission_checker