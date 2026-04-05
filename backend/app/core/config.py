from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    app_name: str = "fincontrol"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fincontrol"
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    upload_dir: str = "./uploads"
    backup_dir: str = "./backups"

    local_demo_mode: bool = True

    # CORS: список origin через запятую. "*" допустим только без cookie — credentials будет принудительно False.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    cors_allow_credentials: bool = True


settings = Settings()
