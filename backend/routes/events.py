from fastapi import APIRouter, Request, Depends
from backend.db import get_connection
from backend.websocket_manager import manager
from fastapi import APIRouter, Depends
from backend.auth import validate_api_key

import asyncio

router = APIRouter()

from backend.auth_jwt import verify_token
from fastapi import Depends

@router.get("/events")
def get_events(user=Depends(verify_token)):
    tenant_id = user["tenant_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, source, raw, created_at FROM events WHERE tenant_id=%s ORDER BY id DESC LIMIT 100",
        (tenant_id,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": r[0],
            "source": r[1],
            "raw": r[2],
            "created_at": str(r[3])
        }
        for r in rows
    ]

@router.post("/events")
async def receive_event(request: Request, user=Depends(verify_token)):
    event = await request.json()
    tenant_id = user["tenant_id"]

    print(f"🔥 EVENT RECEIVED (tenant: {tenant_id})")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO events (source, raw, tenant_id)
            VALUES (%s, %s, %s)
            """,
            (event.get("source"), event.get("raw"), tenant_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ EVENT SAVED IN DB")

    except Exception as e:
        print("❌ DB ERROR:", e)

    asyncio.create_task(manager.broadcast({
        **event,
        "tenant_id": tenant_id
    }))

    return {"status": "stored"}