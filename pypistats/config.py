"""Application configuration."""
import os

from celery.schedules import crontab
from flask import json


def get_db_uri(env):
    """Get the database URI."""
    return \
        "postgresql://{username}:{password}@{host}:{port}/{dbname}".format(
            username=os.environ.get("POSTGRESQL_USERNAME"),
            password=os.environ.get("POSTGRESQL_PASSWORD"),
            host=os.environ.get("POSTGRESQL_HOST"),
            port=os.environ.get("POSTGRESQL_PORT"),
            dbname=os.environ.get("POSTGRESQL_DBNAME"),
        )


class Config(object):
    """Base configuration."""

    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL"),
    CELERY_IMPORTS = ("pypistats.tasks.pypi")
    CELERYBEAT_SCHEDULE = {
        "update_db": {
            "task": "pypistats.tasks.pypi.etl",
            "schedule": crontab(minute=0, hour=1),  # 1am UTC
        },
    }
    GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    SECRET_KEY = os.environ.get("PYPISTATS_SECRET", "secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Plotly chart definitions
    PLOT_BASE = json.load(
        open(os.path.join(os.path.dirname(__file__), "plots", "plot_base.json"))
    )
    DATA_BASE = json.load(
        open(os.path.join(os.path.dirname(__file__), "plots", "data_base.json"))
    )



class ProdConfig(Config):
    """Production configuration."""

    DEBUG = False
    ENV = "prod"
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)


class DevConfig(Config):
    """Development configuration."""

    DEBUG = True
    ENV = "dev"
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)


class TestConfig(Config):
    """Test configuration."""

    DEBUG = True
    ENV = "dev"
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)
    TESTING = True
    WTF_CSRF_ENABLED = False  # Allows form testing


configs = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "test": TestConfig,
}
