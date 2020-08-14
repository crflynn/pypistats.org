"""Run the application."""
import os

from flask import g
from flask import session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from pypistats.application import create_app
from pypistats.application import create_celery
from pypistats.config import configs
from pypistats.models.user import User

# change this for migrations
env = os.environ.get("ENV", "development")

app = create_app(configs[env])

# Rate limiting per IP/worker
app.wsgi_app = ProxyFix(app.wsgi_app)
limiter = Limiter(app, key_func=get_remote_address, application_limits=["5 per second", "30 per minute"])

celery = create_celery(app)

app.logger.info(f"Environment: {env}")


@app.before_request
def before_request():
    """Execute before requests."""
    g.user = None
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])
