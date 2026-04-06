#!/usr/bin/env python3
import json
import os
import random
import string
import sys
import time
from decimal import Decimal
from urllib import error, request

BASE_URL = os.getenv("SMOKE_BASE_URL", "http://localhost:8000").rstrip("/")
EMAIL = os.getenv("SMOKE_TEST_EMAIL", "smoke@example.com")
PASSWORD = os.getenv("SMOKE_TEST_PASSWORD", "SmokePass123!")
TIMEOUT = float(os.getenv("SMOKE_TIMEOUT_SECONDS", "8"))


def _rand_suffix(n=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))


def http_call(method, path, payload=None, token=None, expected=(200, 201), headers=None):
    url = f"{BASE_URL}{path}"
    data = None
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    if token:
        req_headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8")
            parsed = json.loads(body) if body else None
            if resp.status not in expected:
                raise RuntimeError(f"{method} {path} returned {resp.status}, expected {expected}: {parsed}")
            return parsed, resp.status
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(body) if body else None
        except Exception:
            parsed = body
        if exc.code in expected:
            return parsed, exc.code
        raise RuntimeError(f"{method} {path} failed with {exc.code}: {parsed}") from exc


def wait_for_gateway(max_wait=180):
    deadline = time.time() + max_wait
    last_error = None
    while time.time() < deadline:
        try:
            data, _ = http_call("GET", "/api/status", expected=(200,))
            if data.get("overall") in {"ok", "degraded"}:
                return data
        except Exception as exc:
            last_error = exc
        time.sleep(3)
    raise RuntimeError(f"Gateway did not become ready in time. Last error: {last_error}")


def main():
    print(f"[smoke] waiting for gateway at {BASE_URL}")
    status = wait_for_gateway()
    print(f"[smoke] aggregate status: {status.get('overall')}")

    _, _ = http_call("GET", "/health", expected=(200,))

    email = EMAIL
    if email == "smoke@example.com":
        email = f"smoke+{_rand_suffix()}@example.com"

    register_payload = {
        "email": email,
        "password": PASSWORD,
        "full_name": "Smoke Test User",
    }
    user, code = http_call("POST", "/api/v1/auth/register", payload=register_payload, expected=(201, 409))
    if code == 409:
        print("[smoke] user already exists, continuing with login")
    else:
        print(f"[smoke] registered user {user['email']}")

    tokens, _ = http_call("POST", "/api/v1/auth/login", payload={"email": email, "password": PASSWORD}, expected=(200,))
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]
    print("[smoke] login ok")

    refreshed, _ = http_call("POST", "/api/v1/auth/refresh", payload={"refresh_token": refresh}, token=access, expected=(200,))
    access = refreshed["access_token"]
    print("[smoke] refresh ok")

    me, _ = http_call("GET", "/api/v1/users/me", token=access, expected=(200,))
    print(f"[smoke] profile ok: {me['email']}")

    products, _ = http_call("GET", "/api/v1/products?limit=5&offset=0", expected=(200,))
    items = products.get("items", [])
    if not items:
        raise RuntimeError("Catalog returned no products; smoke flow cannot continue")
    product = items[0]
    print(f"[smoke] product ok: {product['name']}")

    cart, _ = http_call(
        "POST",
        "/api/v1/cart/items",
        token=access,
        payload={
            "product_id": product["id"],
            "product_name": product["name"],
            "quantity": 1,
            "unit_price": str(product["price"]),
            "currency": product["currency"],
            "product_slug": product.get("slug"),
            "sku": product.get("sku"),
            "image_url": product.get("image_url"),
        },
        expected=(200, 201),
    )
    print(f"[smoke] cart ok: {cart['items_count']} item(s)")

    order, _ = http_call(
        "POST",
        "/api/v1/orders",
        token=access,
        payload={
            "currency": product["currency"],
            "items": [
                {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "quantity": 1,
                    "unit_price": str(product["price"]),
                    "currency": product["currency"],
                    "product_slug": product.get("slug"),
                    "sku": product.get("sku"),
                }
            ],
            "notes": "Created by smoke test",
        },
        expected=(201,),
    )
    print(f"[smoke] order ok: #{order['id']}")

    payment, _ = http_call(
        "POST",
        "/api/v1/payments/intents",
        token=access,
        payload={
            "order_id": order["id"],
            "amount": str(order["total_amount"]),
            "currency": order["currency"],
            "description": f"Smoke payment for order {order['id']}",
        },
        expected=(201,),
    )
    print(f"[smoke] payment ok: #{payment['id']}")

    inventory, _ = http_call("GET", "/api/v1/inventory?limit=5", token=access, expected=(200,))
    inv_items = inventory.get("items", [])
    if inv_items:
        sku = inv_items[0]["sku"]
        reserved, _ = http_call(
            "POST",
            "/api/v1/inventory/reservations",
            token=access,
            payload={"sku": sku, "quantity": 1, "order_id": order["id"]},
            expected=(200,),
        )
        _, _ = http_call(
            "POST",
            "/api/v1/inventory/reservations/release",
            token=access,
            payload={"sku": sku, "quantity": 1, "order_id": order["id"]},
            expected=(200,),
        )
        print(f"[smoke] inventory ok: reserved on {reserved['sku']}")

    notification, _ = http_call(
        "POST",
        "/api/v1/notifications",
        token=access,
        payload={
            "recipient": email,
            "channel": "email",
            "subject": "Smoke test notification",
            "message": "ShopMesh smoke test completed",
            "related_order_id": order["id"],
            "related_payment_id": payment["id"],
        },
        expected=(201,),
    )
    print(f"[smoke] notification ok: #{notification['id']}")

    summary = {
        "user_email": email,
        "product_id": product["id"],
        "order_id": order["id"],
        "payment_id": payment["id"],
        "notification_id": notification["id"],
    }
    print("[smoke] success")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[smoke] failed: {exc}", file=sys.stderr)
        raise
