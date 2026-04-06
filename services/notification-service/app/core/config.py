from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "notification-service"
    environment: str = "development"
    log_level: str = "INFO"
    port: int = 8007

    database_url: str = "sqlite:///./app.db"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"

    default_sender_email: str = "noreply@shopmesh.local"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
