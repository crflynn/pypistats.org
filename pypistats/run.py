"""Run the application."""
from pypistats.application import create_app
from pypistats.settings import DevConfig
from pypistats.settings import ProdConfig
from pypistats.settings import TestConfig


# change this for migrations
app = create_app(DevConfig)
