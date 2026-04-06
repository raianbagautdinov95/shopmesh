from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "inventory-service"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://shopmesh:shopmesh@postgres:5432/shopmesh"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()