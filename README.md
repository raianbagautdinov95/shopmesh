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

Tech Stack
Backend
FastAPI
SQLAlchemy
Pydantic
Uvicorn
Infrastructure
PostgreSQL
Redis
RabbitMQ
Docker Compose
Nginx
Observability
Prometheus
Grafana
prometheus-fastapi-instrumentator
Implemented Flow

The project currently includes a working end-to-end flow that has been verified with a smoke test:

User registration
User login
Refresh token flow
Fetch current user profile
List products
Add product to cart
Create order
Create payment intent
Fetch inventory
Create notification
Verified Smoke Test

The following flow has been executed successfully against the running stack:

register user
login
refresh token
fetch profile
fetch products
add item to cart
create order
create payment
fetch inventory
create notification

Example successful smoke result:
{
  "user_email": "smoke+example@example.com",
  "product_id": 3,
  "order_id": 5,
  "payment_id": 5,
  "notification_id": 1
}
Quick Start
1. Copy environment file

On Windows CMD:
copy .env.example .env
On PowerShell:
Copy-Item .env.example .env
2. Start the stack
docker compose up --build -d
3. Check running services
docker compose ps
4. Run smoke test

On Windows:

python scripts\smoke_test.py

On Linux/macOS:

python scripts/smoke_test.py
Database Migrations

Alembic has been added for the main domain services. Each service uses its own migration environment and its own Alembic version table.

Services currently migrated
user-service
catalog-service
cart-service
order-service
payment-service
inventory-service
notification-service
Important note

Because multiple services use the same PostgreSQL database, each service must use its own Alembic version table, for example:

alembic_version_user_service
alembic_version_catalog_service
alembic_version_cart_service
alembic_version_order_service
alembic_version_payment_service
alembic_version_inventory_service
alembic_version_notification_service
Run migrations manually

Example pattern:

cd services\<service-name>
python -m alembic upgrade head

Examples:

cd services\user-service
python -m alembic upgrade head
cd services\order-service
python -m alembic upgrade head
cd services\inventory-service
python -m alembic upgrade head
Check current revision
python -m alembic current
Stamp an existing schema

If tables already exist and you want Alembic to mark the current migration as applied:

python -m alembic stamp head
Local Endpoints
API Gateway: http://localhost:8000/docs
Nginx: http://localhost:8080
Auth Service: http://localhost:8001/docs
User Service: http://localhost:8002/docs
Catalog Service: http://localhost:8003/docs
Cart Service: http://localhost:8004/docs
Order Service: http://localhost:8005/docs
Payment Service: http://localhost:8006/docs
Inventory Service: http://localhost:8007/docs
Notification Service: http://localhost:8008/docs
Prometheus: http://localhost:9090
Grafana: http://localhost:3000
RabbitMQ Management: http://localhost:15672
Observability

The project includes a basic observability stack:

Prometheus for metrics scraping
Grafana for dashboards
service-level /metrics endpoints
health endpoints for all services
aggregated gateway status endpoint

Useful endpoints:

Gateway health: http://localhost:8000/health
Gateway aggregate status: http://localhost:8000/api/status
Example Workflow

A typical local workflow looks like this:

Register a new user through the gateway
Log in and receive access and refresh tokens
Fetch available products
Add an item to cart
Create an order
Create a payment intent
Fetch inventory records
Create a notification record
Observe metrics in Prometheus and Grafana
Useful Commands
docker compose up --build -d
docker compose down -v
docker compose ps
docker compose logs -f
python scripts\smoke_test.py
Current State

This project is currently in an actively developed but working state.

Already implemented
microservices structure
gateway routing
authentication flow
user profile flow
catalog flow
cart flow
order flow
payment flow
inventory flow
notification flow
Docker-based local setup
metrics and dashboards
smoke-tested end-to-end scenario
Alembic migrations for core services
Planned next
complete migration coverage for remaining services if needed
stronger integration and contract tests
improved event-driven workflows
better error standardization
more realistic business state transitions
Roadmap
Near term
improve README visuals and architecture diagram
improve service-level tests
refine gateway operation IDs and docs
Mid term
connect order and inventory more deeply
connect payment and notification flows through events
add retry and idempotency patterns
improve gateway-level error handling
Long term
event-driven orchestration
distributed tracing
advanced dashboards
production deployment manifests
Why This Project Matters

This project is designed to demonstrate more than CRUD endpoints. It shows:

microservices decomposition by domain
authentication and protected APIs
gateway-based routing
infrastructure integration
health checks and observability
debugging and stabilization of a full distributed local stack
an end-to-end backend workflow instead of isolated demo endpoints
Notes
The stack is intended for local development and portfolio demonstration.
Some services were originally bootstrapped with lightweight schema setup and are being standardized around Alembic migrations.
Inventory is seeded with demo data for local development and showcase purposes.
License

Add your preferred license here.