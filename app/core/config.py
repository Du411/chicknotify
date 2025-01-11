import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, model_validator, SecretStr
from typing import Optional


current_dir = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(current_dir, "..", "..", ".env"),
        env_file_encoding='utf-8'
    )

    # Database settings
    DB_SERVER: str
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_NAME: str
    DB_PORT: int
    DATABASE_URL: Optional[PostgresDsn] = None

    # Email settings
    GMAIL_SENDER: str
    GMAIL_APP_PASSWORD: SecretStr
    SMTP_SERVER: str
    SMTP_PORT: int

    # Redis settings
    REDIS_SERVER: str
    REDIS_PORT: int
    REDIS_PASSWORD: SecretStr

    # JWT settings
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @model_validator(mode="after")
    def set_database_url(self):
        if not self.DATABASE_URL:
            self.DATABASE_URL = PostgresDsn.build(
                scheme="postgresql",
                username=self.DB_USER,
                password=self.DB_PASSWORD.get_secret_value(),
                host=self.DB_SERVER,
                port=self.DB_PORT,
                path=self.DB_NAME,
            )
        return self

settings = Settings()
