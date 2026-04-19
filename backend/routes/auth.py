from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.db import get_connection
from backend.utils.security import verify_password
from backend.auth_jwt import create_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, password, tenant_id FROM users WHERE username=?",
        (data.username,)
    )

    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    db_username, db_password, tenant_id = user

    if not verify_password(data.password, db_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_token({
        "username": db_username,
        "tenant_id": tenant_id
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }