from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    Values are loaded from environment variables or .env file.
    """

    app_name: str = "receipt-processing"
    app_env: str = "dev"

    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    mongo_uri: str = "mongodb://localhost:27017/receipt_processing"
    mongo_db_name: str = "receipt_processing"

    llm_model_name: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    mcp_server_url: str = "http://localhost:8001"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()