import hashlib, json, sqlite3, uuid
from datetime import datetime, timezone
from .config import AUDIT_DB

def _db():
    con = sqlite3.connect(AUDIT_DB)
    con.execute("""
    CREATE TABLE IF NOT EXISTS audit_events (
      seq INTEGER PRIMARY KEY AUTOINCREMENT,
      event_id TEXT UNIQUE NOT NULL,
      ts_utc TEXT NOT NULL,
      user TEXT NOT NULL,
      project TEXT NOT NULL,
      agent TEXT,
      action TEXT NOT NULL,
      artifacts_json TEXT,
      result TEXT NOT NULL,
      hash_prev TEXT,
      hash_this TEXT NOT NULL
    )
    """)
    return con

def _hash(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

def _tip(con):
    cur = con.cursor()
    cur.execute("SELECT seq, hash_this FROM audit_events ORDER BY seq DESC LIMIT 1")
    row = cur.fetchone()
    return (row[0], row[1]) if row else (0, None)

def append_event_enforced(user, project, action, result, agent=None, artifacts=None):
    con = _db()
    cur = con.cursor()

    ts = datetime.now(timezone.utc).isoformat()
    eid = str(uuid.uuid4())
    last_seq, last_hash = _tip(con)

    payload = {
        "event_id": eid,
        "ts_utc": ts,
        "user": user,
        "project": project,
        "agent": agent,
        "action": action,
        "artifacts": artifacts or {},
        "result": result,
        "hash_prev": last_hash
    }
    h = _hash(payload)

    cur.execute("""
      INSERT INTO audit_events(event_id, ts_utc, user, project, agent, action,
                               artifacts_json, result, hash_prev, hash_this)
      VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (eid, ts, user, project, agent, action, json.dumps(artifacts or {}), result, last_hash, h))

    con.commit()
    con.close()

    payload["hash_this"] = h
    payload["seq"] = last_seq + 1
    return payload

def verify_chain():
    con = _db()
    cur = con.cursor()
    cur.execute("""
      SELECT seq, event_id, ts_utc, user, project, agent, action, artifacts_json, result, hash_prev, hash_this
      FROM audit_events ORDER BY seq ASC
    """)
    rows = cur.fetchall()
    con.close()

    prev = None
    for (seq, eid, ts, user, project, agent, action, aj, result, hprev, hthis) in rows:
        if hprev != prev:
            return {"ok": False, "break_at_seq": seq, "reason": "hash_prev mismatch"}
        payload = {
            "event_id": eid, "ts_utc": ts, "user": user, "project": project,
            "agent": agent, "action": action, "artifacts": json.loads(aj or "{}"),
            "result": result, "hash_prev": hprev
        }
        if _hash(payload) != hthis:
            return {"ok": False, "break_at_seq": seq, "reason": "hash_this mismatch"}
        prev = hthis

    return {"ok": True, "events": len(rows), "tip_hash": prev}
