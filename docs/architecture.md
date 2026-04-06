# Architecture

ShopMesh follows a domain-oriented microservice layout:

- **gateway**: edge routing, auth propagation, rate-limit hooks
- **auth-service**: authentication and JWT issuance
- **user-service**: customer profiles and addresses
- **catalog-service**: products, categories, search
- **cart-service**: shopping carts and items
- **order-service**: order lifecycle
- **payment-service**: payment intents and provider integrations
- **inventory-service**: stock reservations and deductions
- **notification-service**: email / sms / webhook notifications

## Cross-cutting

- PostgreSQL for service persistence
- RabbitMQ for async events
- Redis for caching / ephemeral state
- Prometheus metrics
- Grafana dashboards
