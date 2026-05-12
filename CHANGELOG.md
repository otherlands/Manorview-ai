# Changelog

All notable changes to manorview-ai will be documented in this file.

## [0.1.1] - 2026-05-12

### Added
- `GET /` root route returning service info, version, and endpoint map.
- `GET /healthz` lightweight health probe.
- `VERSION` file (source of truth for build version), copied into Docker image.
- README endpoint reference table.

### Fixed
- Gateway root URL `http://localhost:9000/` previously returned `{"detail":"Not Found"}`.

## [0.1.0] - 2026-05-11

### Added
- Initial scaffold from `bootstrap_manorview_ai.sh`:
  - FastAPI gateway with `/v1/chat/completions`, RAG injection, rate limiting, daily cost cap.
  - Hash-chained audit log (`/audit/event`, `/audit/verify`, `/audit/tip`) backed by SQLite.
  - Prometheus + Grafana via docker compose.
  - VS Code agent pack under `.github/` (PR, Fix, Review, Deploy agents + audit-logging skill).
  - Power Automate daily anchor script.
