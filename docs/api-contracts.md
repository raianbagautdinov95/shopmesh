# API Contracts

All services expose:

- `GET /health`
- `GET /ready`
- `GET /metrics` (placeholder route unless integrated through middleware)

Each business service exposes a versioned router under `/api/v1`.

Gateway proxies or aggregates service APIs through `/api/{service}` in a real deployment. This scaffold keeps gateway endpoints local and ready for expansion.
