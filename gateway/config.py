import os

PROJECT_ID = os.getenv("PROJECT_ID", "manorview-ai")

VLLM_DEEP_BASE_URL = os.getenv("VLLM_DEEP_BASE_URL", "http://192.168.4.20:8000/v1")
VLLM_FAST_BASE_URL = os.getenv("VLLM_FAST_BASE_URL", "http://192.168.4.21:8001/v1")
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "local-token")

AUDIT_DB = os.getenv("AUDIT_DB", "/data/audit.db")

DEFAULT_REQ_PER_MIN = int(os.getenv("DEFAULT_REQ_PER_MIN", "60"))
DEFAULT_COST_UNITS_PER_DAY = int(os.getenv("DEFAULT_COST_UNITS_PER_DAY", "10000"))

RAG_DATA_DIR = os.getenv("RAG_DATA_DIR", "/data/rag/data")
RAG_INDEX_DIR = os.getenv("RAG_INDEX_DIR", "/data/rag/index")
