"""Application configuration."""
import json
import os


# Load env vars
ENV = os.environ.get("ENV", None)

# If none then load dev locally.
if ENV is None:
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "secret",
        "env_vars_dev.json")
    for key, value in json.load(open(local_path, 'r')).items():
        os.environ[key] = value


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
    GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    SECRET_KEY = os.environ.get("PYPISTATS_SECRET", "secret-key")
    SQLALCHEMY_DATABASE_URI = get_db_uri(ENV)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    """Production configuration."""

    DEBUG = False
    ENV = "prod"


class DevConfig(Config):
    """Development configuration."""

    DEBUG = True
    ENV = "dev"


class TestConfig(Config):
    """Test configuration."""

    DEBUG = True
    ENV = "dev"
    TESTING = True
    WTF_CSRF_ENABLED = False  # Allows form testing


configs = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "test": TestConfig,
}
