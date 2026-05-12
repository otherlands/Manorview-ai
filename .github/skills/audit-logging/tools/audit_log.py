import json, os, sys, urllib.request, socket

GATEWAY = os.environ.get("ERIGHT_AUDIT_URL", "http://192.168.4.10:9000/audit/event")
TOKEN = os.environ.get("ERIGHT_USER_TOKEN")
PROJECT = "manorview-ai"

def hostname():
    return socket.gethostname()

def post(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(GATEWAY, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8")

if __name__ == "__main__":
    action = sys.argv[1]
    result = sys.argv[2]
    artifacts = json.loads(sys.argv[3]) if len(sys.argv) > 3 else dict()
    payload = {
        "project": PROJECT,
        "agent": os.environ.get("ERIGHT_AGENT", "unknown"),
        "action": action,
        "result": result,
        "artifacts": artifacts,
        "source_machine": hostname()
    }
    print(post(payload))
