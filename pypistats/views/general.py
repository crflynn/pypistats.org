"""General pages."""
from copy import deepcopy
import os

from flask import Blueprint
from flask import current_app
from flask import g
from flask import json
from flask import redirect
from flask import render_template
from flask_wtf import FlaskForm
import requests
from wtforms import StringField
from wtforms.validators import DataRequired

from pypistats.models.download import OverallDownloadCount
from pypistats.models.download import PythonMajorDownloadCount
from pypistats.models.download import PythonMinorDownloadCount
from pypistats.models.download import RECENT_CATEGORIES
from pypistats.models.download import RecentDownloadCount
from pypistats.models.download import SystemDownloadCount


blueprint = Blueprint("general", __name__, template_folder="templates")


MODELS = [
    OverallDownloadCount,
    PythonMajorDownloadCount,
    PythonMinorDownloadCount,
    SystemDownloadCount,
]


class MyForm(FlaskForm):
    """Search form."""

    name = StringField("Package: ", validators=[DataRequired()])


@blueprint.route("/", methods=("GET", "POST"))
def index():
    """Render the home page."""
    form = MyForm()
    if form.validate_on_submit():
        package = form.name.data
        return redirect(f"/search/{package}")
    return render_template("index.html", form=form, user=g.user)


@blueprint.route("/search/<package>", methods=("GET", "POST"))
def search(package):
    """Render the home page."""
    form = MyForm()
    if form.validate_on_submit():
        package = form.name.data
        return redirect(f"/search/{package}")
    results = RecentDownloadCount.query.filter(
        RecentDownloadCount.package.like(f"{package}%"),
        RecentDownloadCount.category == "month").\
        order_by(RecentDownloadCount.package).\
        limit(20).all()
    packages = [r.package for r in results]
    return render_template(
        "search.html", search=True, form=form, packages=packages, user=g.user
    )


@blueprint.route("/about")
def about():
    """Render the about page."""
    return render_template("about.html", user=g.user)


@blueprint.route("/package/<package>")
def package(package):
    """Render the package page."""
    # PyPI metadata
    try:
        metadata = requests.get(
            f"https://pypi.python.org/pypi/{package}/json").json()
    except Exception:
        metadata = None

    # Get data from db
    model_data = []
    for model in MODELS:
        model_data.append({
            "name": model.__tablename__,
            "data": get_download_data(package, model),
        })

    # Plotly chart definitions
    plot_base = json.load(
        open(os.path.join(current_app.root_path, 'plots', 'plot_base.json'))
    )
    data_base = json.load(
        open(os.path.join(current_app.root_path, 'plots', 'data_base.json'))
    )

    # Build the plots
    plots = []
    for model in model_data:
        plot = deepcopy(plot_base)
        data = []
        for category, values in model["data"].items():
            base = deepcopy(data_base)
            base["x"] = values["x"]
            base["y"] = values["y"]
            base["name"] = category.title()
            data.append(base)
        plot["data"] = data
        plot["layout"]["title"] = \
            f"Downloads by {model['name'].title().replace('_', ' ')}"
        plots.append(plot)

    # Recent download stats
    recent_downloads = RecentDownloadCount.query.\
        filter_by(package=package).all()
    recent = {r: 0 for r in RECENT_CATEGORIES}
    for r in recent_downloads:
        recent[r.category] = r.downloads

    return render_template(
        "package.html",
        package=package,
        plots=plots,
        metadata=metadata,
        recent=recent,
        user=g.user
    )


def get_download_data(package, model):
    """Get the download data for a package - model."""
    records = model.query.filter_by(package=package).\
        order_by(model.category,
                 model.date).all()
    data = {}
    for record in records:
        category = record.category
        if category not in data:
            data[category] = {"x": [], "y": []}
        data[category]["x"].append(str(record.date))
        data[category]["y"].append(record.downloads)
    return data


@blueprint.route("/top")
def top():
    """Render the top packages page."""
    top = []
    for category in ("day", "week", "month"):
        downloads = RecentDownloadCount.query.filter_by(category=category).\
            filter(RecentDownloadCount.package != "__all__").\
            order_by(RecentDownloadCount.downloads.desc()).limit(20).all()
        top.append({
            "category": category,
            "packages": [{
                "package": d.package,
                "downloads": d.downloads,
            } for d in downloads]
        })
    return render_template("top.html", top=top, user=g.user)


@blueprint.route("/status")
def status():
    """Return OK."""
    return "OK"
