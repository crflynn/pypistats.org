"""User page for tracking packages."""
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from pypistats.extensions import db
from pypistats.extensions import github
from pypistats.models.user import User

blueprint = Blueprint('user', __name__, template_folder='templates')


@blueprint.route("/user/<user>")
def user(user):
    """Render the user's personal page."""
    return user + "'s page"


@blueprint.route("/user/<user>/package/<package>", methods=['POST', 'DELETE'])
def user_package(user):
    """Handle adding and deleting packages to user's list."""
    return "SOMETHING"


@blueprint.route('/login')
def login():
    """Login."""
    return github.authorize()


@blueprint.route('/logout')
def logout():
    """Logout."""
    session.pop('user_id', None)
    return redirect(url_for('index'))


@blueprint.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    """Github authorization callback."""
    next_url = request.args.get('next') or url_for('index')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)

    user = User.query.filter_by(token=oauth_token).first()
    if user is None:
        user = User(oauth_token)
        db.add(user)

    user.github_access_token = oauth_token
    db.commit()
    return redirect(next_url)


@github.access_token_getter
def token_getter():
    """Get the token for a user."""
    user = g.user
    if user is not None:
        return user.github_access_token
