import os, requests

GATEWAY = os.environ.get("GATEWAY_URL", "http://192.168.4.10:9000")
FLOW = os.environ.get("ERIGHT_TEAMS_FLOW_URL", "")

def main():
    tip = requests.get(f"{GATEWAY}/audit/tip", timeout=10).json().get("tip_hash")
    if not FLOW:
        print("No ERIGHT_TEAMS_FLOW_URL set")
        return
    payload = {
        "event": "daily_anchor",
        "project": "manorview-ai",
        "user": "system",
        "pr_url": "-",
        "commit": "-",
        "tip_hash": tip or ""
    }
    requests.post(FLOW, json=payload, timeout=10)
    print("Anchored tip hash to Teams")

if __name__ == "__main__":
    main()
