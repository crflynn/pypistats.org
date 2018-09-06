"""Run the application."""
import os

from flask import g
from flask import session
from flask_sslify import SSLify

from pypistats.application import create_app
from pypistats.application import create_celery
from pypistats.extensions import db
from pypistats.models.user import User
from pypistats.settings import configs


# change this for migrations
env = os.environ.get("ENV", "dev")

app = create_app(configs[env])
sslify = SSLify(app)
celery = create_celery(app)

app.logger.info(f"Environment: {env}")


@app.before_request
def before_request():
    """Execute before requests."""
    g.user = None
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])
    if "db" not in g:
        g.db = db
