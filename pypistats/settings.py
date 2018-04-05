"""Application configuration."""
import os

from pypistats.secret import postgresql


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
    GITHUB_CLIENT_ID = "test"
    GITHUB_CLIENT_SECRET = "test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    """Production configuration."""

    ENV = "prod"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)


class DevConfig(Config):
    """Development configuration."""

    ENV = "dev"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)


class TestConfig(Config):
    """Test configuration."""

    ENV = "dev"
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)
    WTF_CSRF_ENABLED = False  # Allows form testing
