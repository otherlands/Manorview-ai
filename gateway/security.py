import os
from fastapi import Request, HTTPException

BOOTSTRAP_ADMIN_KEY = os.getenv("BOOTSTRAP_ADMIN_KEY", "change-me-admin")
BOOTSTRAP_KEYS = {BOOTSTRAP_ADMIN_KEY: "admin@eright.local"}

def _bearer(req: Request) -> str:
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return ""
    return auth.split(" ", 1)[1].strip()

def resolve_user(req: Request) -> str:
    token = _bearer(req)
    if not token:
        raise HTTPException(401, "Missing bearer token")
    if token in BOOTSTRAP_KEYS:
        return BOOTSTRAP_KEYS[token]
    raise HTTPException(403, "Invalid API key")
