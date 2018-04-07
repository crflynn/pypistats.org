"""Application configuration."""
import os

from pypistats.secret import postgresql
from pypistats.secret import github


def get_db_uri(env):
    """Get the database URI."""
    return \
        "postgresql://{username}:{password}@{host}:{port}/{dbname}".format(
            username=postgresql[env]["username"],
            password=postgresql[env]["password"],
            host=postgresql[env]["host"],
            port=postgresql[env]["port"],
            dbname=postgresql[env]["dbname"],
        )


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get("PYPISTATS_SECRET", "secret-key")
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    """Production configuration."""

    ENV = "prod"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)
    GITHUB_CLIENT_ID = github[ENV]["client_id"]
    GITHUB_CLIENT_SECRET = github[ENV]["client_secret"]


class DevConfig(Config):
    """Development configuration."""

    ENV = "dev"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)
    GITHUB_CLIENT_ID = github[ENV]["client_id"]
    GITHUB_CLIENT_SECRET = github[ENV]["client_secret"]


class TestConfig(Config):
    """Test configuration."""

    ENV = "dev"
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)
    WTF_CSRF_ENABLED = False  # Allows form testing
    GITHUB_CLIENT_ID = github[ENV]["client_id"]
    GITHUB_CLIENT_SECRET = github[ENV]["client_secret"]
