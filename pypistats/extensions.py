"""Flask extensions."""
from flask_github import GitHub
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
github = GitHub()
migrate = Migrate()
