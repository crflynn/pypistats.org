"""Error page handlers."""
from flask import Blueprint

blueprint = Blueprint('error', __name__, template_folder='templates')


@blueprint.app_errorhandler(400)
def handle_400(err):
    """Return 400."""
    return "400", 400


@blueprint.app_errorhandler(401)
def handle_401(err):
    """Return 401."""
    return "401", 401


@blueprint.app_errorhandler(404)
def handle_404(err):
    """Return 404."""
    return "404", 404


@blueprint.app_errorhandler(500)
def handle_500(err):
    """Return 500."""
    return "500", 500


@blueprint.app_errorhandler(503)
def handle_503(err):
    """Return 500."""
    return "503 TEMPORARILY DISABLED", 503
