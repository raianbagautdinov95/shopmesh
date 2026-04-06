from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "gateway"
    environment: str = "development"
    log_level: str = "INFO"
    port: int = 8000

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    request_timeout: float = 10.0

    auth_service_url: str = "http://auth-service:8001"
    user_service_url: str = "http://user-service:8002"
    catalog_service_url: str = "http://catalog-service:8003"
    cart_service_url: str = "http://cart-service:8004"
    order_service_url: str = "http://order-service:8005"
    payment_service_url: str = "http://payment-service:8006"
    inventory_service_url: str = "http://inventory-service:8007"
    notification_service_url: str = "http://notification-service:8008"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()