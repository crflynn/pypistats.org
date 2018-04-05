"""PyPIStats application."""
from flask import Flask

from pypistats import views
from pypistats.extensions import db
from pypistats.extensions import github
from pypistats.extensions import migrate
from pypistats.settings import DevConfig
from pypistats.settings import ProdConfig
from pypistats.settings import TestConfig


def create_app(config_object=DevConfig):
    """Create the application.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    github.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(views.api.blueprint)
    app.register_blueprint(views.error.blueprint)
    app.register_blueprint(views.general.blueprint)
    app.register_blueprint(views.user.blueprint)
