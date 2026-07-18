# ShopMesh

ShopMesh is a production-style microservices e-commerce backend built with FastAPI, PostgreSQL, Redis, RabbitMQ, Prometheus, and Grafana.

The project focuses on clear domain separation, API gateway routing, authentication, service-to-service communication, observability, and a real end-to-end commerce flow.

## Features

- API Gateway for centralized routing
- JWT authentication with access and refresh tokens
- User profile service
- Product catalog service
- Cart management
- Order creation
- Payment intent flow
- Inventory service
- Notification service
- PostgreSQL persistence
- Redis integration
- RabbitMQ integration
- Prometheus metrics
- Grafana dashboards
- Docker Compose local environment
- End-to-end smoke-tested flow

## Services

- `gateway`
- `auth-service`
- `user-service`
- `catalog-service`
- `cart-service`
- `order-service`
- `payment-service`
- `inventory-service`
- `notification-service`

## Architecture Overview

ShopMesh is organized as a set of domain-focused microservices behind a single API gateway.

```text
Client
  -> Nginx
  -> Gateway
      -> Auth Service
      -> User Service
      -> Catalog Service
      -> Cart Service
      -> Order Service
      -> Payment Service
      -> Inventory Service
      -> Notification Service

Services
  -> PostgreSQL
  -> Redis
  -> RabbitMQ

Prometheus
  -> scrapes service metrics

Grafana
  -> visualizes metrics and dashboards
```
## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### Infrastructure

- PostgreSQL
- Redis
- RabbitMQ
- Docker Compose
- Nginx

### Observability

- Prometheus
- Grafana
- prometheus-fastapi-instrumentator

## Implemented Flow

The project includes a working end-to-end commerce flow:

1. User registration
2. User login
3. Refresh token flow
4. Fetch current user profile
5. List products
6. Add product to cart
7. Create order
8. Create payment intent
9. Fetch inventory
10. Create notification

## Verified Smoke Test

The full flow has been executed successfully against the running stack.

Example result:

```json
{
  "user_email": "smoke+example@example.com",
  "product_id": 3,
  "order_id": 5,
  "payment_id": 5,
  "notification_id": 1
}
```

## Quick Start

### 1. Copy the environment file

Windows CMD:

```cmd
copy .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

### 2. Start the stack

```bash
docker compose up --build -d
```

### 3. Check the running services

```bash
docker compose ps
```

### 4. Run the smoke test

```bash
python scripts/smoke_test.py
```

## Database Migrations

Each main domain service has its own Alembic migration environment and version table.

Services with migrations:

- `user-service`
- `catalog-service`
- `cart-service`
- `order-service`
- `payment-service`
- `inventory-service`
- `notification-service`

Because several services currently share one PostgreSQL database, every service uses a separate Alembic version table.

Examples:

```text
alembic_version_user_service
alembic_version_catalog_service
alembic_version_cart_service
alembic_version_order_service
alembic_version_payment_service
alembic_version_inventory_service
alembic_version_notification_service
```

Run migrations for a service:

```bash
cd services/<service-name>
python -m alembic upgrade head
```

Example:

```bash
cd services/user-service
python -m alembic upgrade head
```

Check the current revision:

```bash
python -m alembic current
```

Mark an existing schema as migrated:

```bash
python -m alembic stamp head
```

## Local Endpoints

| Component | URL |
|---|---|
| API Gateway | `http://localhost:8000/docs` |
| Nginx | `http://localhost:8080` |
| Auth Service | `http://localhost:8001/docs` |
| User Service | `http://localhost:8002/docs` |
| Catalog Service | `http://localhost:8003/docs` |
| Cart Service | `http://localhost:8004/docs` |
| Order Service | `http://localhost:8005/docs` |
| Payment Service | `http://localhost:8006/docs` |
| Inventory Service | `http://localhost:8007/docs` |
| Notification Service | `http://localhost:8008/docs` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` |
| RabbitMQ Management | `http://localhost:15672` |

## Observability

The project includes:

- Prometheus metrics scraping
- Grafana dashboards
- service-level `/metrics` endpoints
- health endpoints for all services
- an aggregated gateway status endpoint

Useful endpoints:

```text
http://localhost:8000/health
http://localhost:8000/api/status
```

## Example Workflow

A typical local workflow is:

1. Register a user through the gateway
2. Log in and receive access and refresh tokens
3. Fetch available products
4. Add an item to the cart
5. Create an order
6. Create a payment intent
7. Fetch inventory records
8. Create a notification
9. Observe metrics in Prometheus and Grafana

## Useful Commands

```bash
docker compose up --build -d
docker compose down -v
docker compose ps
docker compose logs -f
python scripts/smoke_test.py
```

## Current State

The project is actively developed and has a working local end-to-end flow.

### Implemented

- microservices structure
- API gateway routing
- JWT authentication
- user profile flow
- product catalog flow
- cart flow
- order flow
- payment flow
- inventory flow
- notification flow
- Docker-based local environment
- Prometheus and Grafana monitoring
- smoke-tested end-to-end scenario
- Alembic migrations for main services

### Planned Improvements

- stronger integration and contract tests
- improved event-driven workflows
- standardized error handling
- retry and idempotency patterns
- distributed tracing
- production deployment manifests

## Why This Project Matters

This project demonstrates more than isolated CRUD endpoints. It shows:

- domain-based microservice decomposition
- authentication and protected APIs
- gateway-based routing
- database and infrastructure integration
- health checks and observability
- debugging of a distributed local stack
- a complete backend commerce workflow

## Notes

The stack is intended for local development and portfolio demonstration.

Some services were initially bootstrapped with lightweight schema creation and are being standardized around Alembic migrations.

Inventory is seeded with demonstration data.

## License

This project is currently provided for portfolio and educational purposes.
