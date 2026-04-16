from fastapi import Header, HTTPException

# 🔐 API KEYS (puedes luego mover esto a DB)
API_KEYS = {
    "abc123securekey": {
        "tenant_id": "company_a"
    }
}

# ==============================
# 🔐 VALIDAR API KEY
# ==============================
def validate_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key missing")

    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return API_KEYS[x_api_key]