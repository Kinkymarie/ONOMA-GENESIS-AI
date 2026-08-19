from __future__ import annotations
import os
from pathlib import Path

class Settings:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DB_PATH: Path = Path(os.getenv("ONOMA_DB_PATH", BASE_DIR / "data" / "onoma.db"))
    UPLOAD_LIMIT_BYTES: int = int(os.getenv("ONOMA_UPLOAD_MAX_BYTES", 5_000_000))
    ENV: str = os.getenv("ONOMA_ENV", "development")
    PROVIDER_API_KEY: str | None = os.getenv("ONOMA_PROVIDER_API_KEY")
    LOG_LEVEL: str = os.getenv("ONOMA_LOG_LEVEL", "INFO")

settings = Settings()
