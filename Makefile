SHELL := /bin/bash

SERVICES = gateway auth-service user-service catalog-service cart-service order-service payment-service inventory-service notification-service

.PHONY: bootstrap up down logs lint format test

bootstrap:
	bash scripts/bootstrap.sh

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

lint:
	for service in $(SERVICES); do \
		if [ -f services/$$service/pyproject.toml ]; then \
			(cd services/$$service && python -m ruff check app tests); \
		fi; \
	done

format:
	bash scripts/format.sh

test:
	for service in $(SERVICES); do \
		if [ -f services/$$service/pyproject.toml ]; then \
			(cd services/$$service && python -m pytest -q); \
		fi; \
	done


smoke:
	python scripts/smoke_test.py

ps:
	docker compose ps