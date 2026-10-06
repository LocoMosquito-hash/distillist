# backend/app/config.py


import logging
from functools import lru_cache

from pydantic import AnyUrl, SecretStr
from pydantic_settings import BaseSettings


log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: AnyUrl = None
    spotify_client_id: str
    spotify_client_secret: SecretStr
    spotify_redirect_uri: str
    frontend_url: str = "http://127.0.0.1:5173"  # where the browser lands after logging in
    token_encryption_key: SecretStr
    session_secret_key: SecretStr
    session_ttl_seconds: int = 60 * 60 * 24 * 7  # 7 days


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()