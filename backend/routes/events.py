from fastapi import APIRouter, Request, Depends
from backend.db import get_connection, normalize_query
from backend.websocket_manager import manager

import asyncio
import json
import os

router = APIRouter()

from backend.auth_jwt import verify_token

@router.get("/events")
def get_events(user=Depends(verify_token)):
    tenant_id = user["tenant_id"]

    conn = get_connection()
    cursor = conn.cursor()

    query = normalize_query(
        "SELECT id, source, raw, created_at FROM events WHERE tenant_id=%s ORDER BY id DESC LIMIT 100"
    )
    cursor.execute(query, (tenant_id,))

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

        query = normalize_query(
            "INSERT INTO events (source, raw, tenant_id) VALUES (%s, %s, %s)"
        )
        cursor.execute(query, (event.get("source"), event.get("raw"), tenant_id))

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ EVENT SAVED IN DB")

    except Exception as e:
        print("❌ DB ERROR:", e)

    try:
        asyncio.create_task(manager.broadcast({
            **event,
            "tenant_id": tenant_id
        }))
    except Exception as e:
        print(f"⚠️ WebSocket broadcast error: {e}")

    return {"status": "stored"}