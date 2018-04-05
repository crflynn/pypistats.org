"""General pages."""
from flask import Blueprint

from pypistats.models.download import OverallDownloadCount
from pypistats.models.download import PythonMajorDownloadCount
from pypistats.models.download import PythonMinorDownloadCount
from pypistats.models.download import SystemDownloadCount


blueprint = Blueprint('general', __name__, template_folder='templates')


@blueprint.route("/")
def index():
    """Render the home page."""
    return "PYPISTATS!"


@blueprint.route("/about")
def about():
    """Render the about page."""
    return "About this website."


@blueprint.route("/<package>")
def package(package):
    """Render the package page."""
    return package + ' main page'


@blueprint.route("/top")
def top():
    """Render the top packages page."""
    return 'top stats'


@blueprint.route("/status")
def status():
    """Return OK."""
    return "OK"
