# manorview-ai — Enterprise AI Gateway (vLLM + RAG + Audit)

**Version:** see [`VERSION`](VERSION)

This repo bootstraps an on‑prem AI platform:

- Local inference via vLLM (deep + fast)
- OpenAI-compatible gateway `/v1/chat/completions` with RAG injection
- Hash-chained audit log (`/audit/event`, `/audit/verify`, `/audit/tip`)
- Prometheus + Grafana monitoring (vLLM exposes `/metrics`)
- VS Code agent pack under `.github/`

## Endpoints (gateway, port 9000)
- `GET  /`              — service info + version
- `GET  /healthz`       — health probe
- `GET  /metrics`       — Prometheus metrics
- `GET  /audit/verify`  — verify full hash chain
- `GET  /audit/tip`     — current tip hash
- `POST /audit/event`   — append audit event (Bearer auth)
- `POST /v1/chat/completions` — OpenAI-compatible chat (Bearer auth)
- `GET  /docs`          — Swagger UI

## Network
- AI VLAN: 192.168.4.0/24
- Users VLAN: 172.16.15.0/24
- VPN VLAN: 192.168.50.0/24
- Gateway: 192.168.4.10:9000

## Quick start
```bash
cp .env.example .env
# edit .env (keys + flow URL)
docker compose up -d --build
```
