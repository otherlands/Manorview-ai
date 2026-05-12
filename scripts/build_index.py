import os, json
import faiss
from sentence_transformers import SentenceTransformer

DATA_DIR = os.environ.get("RAG_DATA_DIR", "/data/rag/data")
INDEX_DIR = os.environ.get("RAG_INDEX_DIR", "/data/rag/index")

EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_BYTES = 3000
EXTS = (".py",".js",".ts",".md",".json",".yaml",".yml",".txt")

def iter_files(root):
    for base, _, files in os.walk(root):
        for f in files:
            if f.endswith(EXTS):
                yield os.path.join(base, f)

def main():
    os.makedirs(INDEX_DIR, exist_ok=True)
    embed = SentenceTransformer(EMBED_MODEL)
    meta, chunks = [], []

    for path in iter_files(DATA_DIR):
        try:
            b = open(path, "rb").read()
            for start in range(0, len(b), CHUNK_BYTES):
                end = min(len(b), start + CHUNK_BYTES)
                txt = b[start:end].decode("utf-8", errors="ignore")
                if txt.strip():
                    chunks.append(txt)
                    meta.append({"path": path, "start": start, "end": end})
        except Exception:
            pass

    if not chunks:
        print("No chunks indexed. Put repo under RAG_DATA_DIR.")
        return

    vecs = embed.encode(chunks)
    index = faiss.IndexFlatL2(len(vecs[0]))
    index.add(vecs)

    faiss.write_index(index, os.path.join(INDEX_DIR, "code.index"))
    json.dump(meta, open(os.path.join(INDEX_DIR, "meta.json"), "w", encoding="utf-8"))
    print("Indexed", len(meta), "chunks")

if __name__ == "__main__":
    main()
