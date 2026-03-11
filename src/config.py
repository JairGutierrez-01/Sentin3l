import os
from pathlib import Path
from dotenv import load_dotenv

# Finds the Path of the project (where.env is)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    PROJECT_NAME: str = "Sentin3l"
    VERSION: str = "0.1.0"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-insecure-key")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"


settings = Settings()