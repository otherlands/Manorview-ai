import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .config import PROJECT_ID, DEFAULT_REQ_PER_MIN, DEFAULT_COST_UNITS_PER_DAY, VLLM_DEEP_BASE_URL, VLLM_FAST_BASE_URL
from .security import resolve_user
from .ratelimit import RateLimiter
from .telemetry import GATEWAY_REQUESTS, AUDIT_CHAIN_OK, timer
from .audit import append_event_enforced, verify_chain
from .rag import RAGIndex
from .models import client_for

def _read_version() -> str:
    for p in ("/app/VERSION", os.path.join(os.path.dirname(__file__), "..", "VERSION")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            continue
    return "0.0.0"

VERSION = _read_version()

app = FastAPI(title=f"{PROJECT_ID} Gateway", version=VERSION)
limiter = RateLimiter()
rag = RAGIndex()
rag.load()
_cost = {}

@app.get("/")
def root():
    return {
        "service": f"{PROJECT_ID} Gateway",
        "version": VERSION,
        "status": "ok",
        "endpoints": {
            "health": "/healthz",
            "metrics": "/metrics",
            "audit_verify": "/audit/verify",
            "audit_tip": "/audit/tip",
            "audit_event": "POST /audit/event",
            "chat": "POST /v1/chat/completions",
            "docs": "/docs"
        }
    }

@app.get("/healthz")
def healthz():
    return {"ok": True, "version": VERSION, "project": PROJECT_ID}

def _rag_inject(messages, query_text: str):
    chunks = rag.retrieve(query_text, k=6)
    if not chunks:
        return messages
    ctx = "\n\n".join([f"FILE: {c['path']}\n{c['chunk']}" for c in chunks])
    sys = {"role": "system", "content": "Use repo context:\n\n" + ctx}
    return [sys] + messages

@app.get("/metrics")
def metrics():
    v = verify_chain()
    AUDIT_CHAIN_OK.set(1 if v.get("ok") else 0)
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

@app.get("/audit/verify")
def audit_verify():
    return verify_chain()

@app.get("/audit/tip")
def audit_tip():
    v = verify_chain()
    return {"ok": v.get("ok"), "tip_hash": v.get("tip_hash")}

@app.post("/audit/event")
async def audit_event(req: Request):
    user = resolve_user(req)
    body = await req.json()
    for k in ("project", "action", "result"):
        if k not in body:
            raise HTTPException(400, "project, action, result required")
    return append_event_enforced(user, body["project"], body["action"], body["result"], body.get("agent"), body.get("artifacts", {}))

@app.post("/v1/chat/completions")
async def chat(req: Request):
    user = resolve_user(req)

    if not limiter.allow(user, DEFAULT_REQ_PER_MIN):
        GATEWAY_REQUESTS.labels(status="rate_limited").inc()
        raise HTTPException(429, "Rate limit exceeded")

    body = await req.json()
    messages = body.get("messages")
    if not messages:
        raise HTTPException(400, "messages[] required")

    query = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            query = m.get("content", "")
            break

    _cost[user] = _cost.get(user, 0) + 1
    if _cost[user] > DEFAULT_COST_UNITS_PER_DAY:
        raise HTTPException(429, "Daily budget exceeded")

    model = body.get("model", "local-vllm-deep")
    base = VLLM_DEEP_BASE_URL if model.endswith("deep") else VLLM_FAST_BASE_URL
    client = client_for(base)

    with timer():
        injected = _rag_inject(messages, query)
        resp = client.chat.completions.create(
            model=body.get("upstream_model", "Qwen/Qwen2.5-Coder-14B-Instruct"),
            messages=injected,
            temperature=body.get("temperature", 0.2),
        )

    append_event_enforced(user, PROJECT_ID, "chat_completion", "success", "gateway", {"model": model, "base_url": base})
    GATEWAY_REQUESTS.labels(status="ok").inc()
    return resp.model_dump()
