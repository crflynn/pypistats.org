"""Run the application."""
import os

from flask import g
from flask import session
from flask_sslify import SSLify

from pypistats.application import create_app
from pypistats.application import create_celery
from pypistats.config import configs
from pypistats.models.user import User

# change this for migrations
env = os.environ.get("ENV", "development")

app = create_app(configs[env])
if env in ("production", "staging"):
    sslify = SSLify(app)
celery = create_celery(app)

app.logger.info(f"Environment: {env}")


@app.before_request
def before_request():
    """Execute before requests."""
    g.user = None
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])
