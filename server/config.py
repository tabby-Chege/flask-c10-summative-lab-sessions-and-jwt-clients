import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///notes.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "local-development-secret-key-change-before-deployment-2026",
    )
