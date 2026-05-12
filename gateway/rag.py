import os, json
import faiss
from sentence_transformers import SentenceTransformer
from .config import RAG_INDEX_DIR

EMBED_MODEL = "all-MiniLM-L6-v2"

class RAGIndex:
    def __init__(self):
        self.embed = SentenceTransformer(EMBED_MODEL)
        self.index_path = os.path.join(RAG_INDEX_DIR, "code.index")
        self.meta_path = os.path.join(RAG_INDEX_DIR, "meta.json")
        self._index = None
        self._meta = None

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self._index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self._meta = json.load(f)

    def retrieve(self, query: str, k: int = 6):
        if self._index is None or self._meta is None:
            return []
        q = self.embed.encode([query])
        _, I = self._index.search(q, k)
        out = []
        for idx in I[0]:
            if idx < 0 or idx >= len(self._meta):
                continue
            item = self._meta[idx]
            try:
                with open(item["path"], "rb") as f:
                    f.seek(item["start"])
                    chunk = f.read(item["end"] - item["start"]).decode("utf-8", errors="ignore")
                out.append({"path": item["path"], "chunk": chunk})
            except Exception:
                pass
        return out
