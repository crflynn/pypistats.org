"""Run the application."""
import os

from flask import g
from flask import session

from pypistats.application import create_app
from pypistats.models.user import User
from pypistats.settings import DevConfig
from pypistats.settings import ProdConfig
from pypistats.settings import TestConfig


# change this for migrations
app = create_app(DevConfig)


@app.before_request
def before_request():
    """Execute before requests."""
    g.user = None
    if "user_id" in session:
        g.user = User.query.get(session['user_id'])
