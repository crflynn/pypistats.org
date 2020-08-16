import os

from flask import Blueprint
from flask import render_template
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from wtforms import DateField
from wtforms.validators import DataRequired

from pypistats.extensions import auth
from pypistats.tasks.pypi import etl

users = {os.environ["BASIC_AUTH_USER"]: generate_password_hash(os.environ["BASIC_AUTH_PASSWORD"])}


blueprint = Blueprint("admin", __name__, template_folder="templates")


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


class BackfillDateForm(FlaskForm):
    date = DateField("Date: ", validators=[DataRequired()])


@blueprint.route("/admin", methods=("GET", "POST"))
@auth.login_required
def index():
    form = BackfillDateForm()
    if form.validate_on_submit():
        date = form.date.data
        etl.apply_async(args=(str(date),))
        return render_template("admin.html", form=form, date=date)
    return render_template("admin.html", form=form)
