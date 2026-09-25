import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Base config — shared across environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Database — Neon in production, SQLite for quick local dev if needed
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "instance", "portfolio.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # Neon drops idle connections — this reconnects
        "pool_recycle": 300,     # recycle every 5 min
    }

    # Admin credentials (set in .env)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")

    ## ── File Storage ──
    STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local")

    # Local upload paths
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    LOCAL_UPLOAD_URL_PREFIX = "/static/uploads"

    # Cloudflare R2
    R2_ACCOUNT_ID = os.environ.get("R2_ACCOUNT_ID", "")
    R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "")
    R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME", "")
    R2_PUBLIC_URL = os.environ.get("R2_PUBLIC_URL", "")  # e.g. https://pub-xxx.r2.dev

    # Upload constraints
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf"}

    # Contact form
    CONTACT_RECIPIENT = os.environ.get("CONTACT_RECIPIENT", "")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # Force HTTPS cookies when deployed behind Render's proxy
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}