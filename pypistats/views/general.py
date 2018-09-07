"""General pages."""
from collections import defaultdict
from copy import deepcopy
import datetime
import os
import re

from flask import abort
from flask import Blueprint
from flask import current_app
from flask import g
from flask import json
from flask import redirect
from flask import render_template
from flask_wtf import FlaskForm
import requests
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy.sql.expression import label
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
        return redirect(f"/search/{package.lower()}")
    package_count = \
        RecentDownloadCount.query.filter_by(category="month").count()
    return render_template(
        "index.html",
        form=form,
        user=g.user,
        package_count=package_count
    )


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


@blueprint.route("/faqs")
def faqs():
    """Render the FAQs page."""
    return render_template("faqs.html", user=g.user)


@blueprint.route("/packages/<package>")
def package(package):
    """Render the package page."""
    # Recent download stats
    recent_downloads = RecentDownloadCount.query.\
        filter_by(package=package).all()
    if len(recent_downloads) == 0:
        abort(404)
    recent = {r: 0 for r in RECENT_CATEGORIES}
    for r in recent_downloads:
        recent[r.category] = r.downloads

    # PyPI metadata
    metadata = None
    if package != "__all__":
        try:
            metadata = requests.get(
                f"https://pypi.python.org/pypi/{package}/json",
                timeout=5).json()
            if metadata["info"].get("requires_dist", None):
                metadata["requires"] = []
                for required in metadata["info"]["requires_dist"]:
                    metadata["requires"].append(
                        re.split(r"[^0-9a-zA-Z_.-]+", required)[0]
                    )
        except Exception:
            pass

    # Get data from db
    model_data = []
    for model in MODELS:
        records = model.query.filter_by(package=package).\
            order_by(model.date,
                     model.category).all()

        if model == OverallDownloadCount:
            metrics = ["downloads"]
        else:
            metrics = ["downloads", "percentages"]

        for metric in metrics:
            model_data.append({
                "metric": metric,
                "name": model.__tablename__,
                "data": data_function[metric](records),
            })

    # Build the plots
    plots = []
    for model in model_data:
        plot = deepcopy(current_app.config["PLOT_BASE"])[model["metric"]]
        data = []
        for category, values in model["data"].items():
            base = deepcopy(current_app.config["DATA_BASE"][model["metric"]]["data"][0])
            base["x"] = values["x"]
            base["y"] = values["y"]
            if model["metric"] == "percentages":
                base["text"] = values["text"]
            base["name"] = category.title()
            data.append(base)
        plot["data"] = data
        plot["layout"]["title"] = \
            f"Downloads of {package} package - {model['name'].title().replace('_', ' ')}"  # noqa
        plots.append(plot)
    return render_template(
        "package.html",
        package=package,
        plots=plots,
        metadata=metadata,
        recent=recent,
        user=g.user
    )

def get_download_data(records):
    """Get the download data for a package - model."""
    data = defaultdict(lambda: {"x": [], "y": []})

    date_categories = []
    all_categories = []

    prev_date = records[0].date

    for record in records:
        if record.category not in all_categories:
            all_categories.append(record.category)

    all_categories = sorted(all_categories)
    for category in all_categories:
        data[category]  # set the dict value (keeps it ordered)

    for record in records:
        # Fill missing intermediate dates with zeros
        if record.date != prev_date:

            for category in all_categories:
                if category not in date_categories:
                    data[category]["x"].append(str(prev_date))
                    data[category]["y"].append(0)

            # Fill missing intermediate dates with zeros
            days_between = (record.date - prev_date).days
            date_list = [prev_date + datetime.timedelta(days=x) for x in range(1, days_between)]

            for date in date_list:
                for category in all_categories:
                    data[category]["x"].append(str(date))
                    data[category]["y"].append(0)

            # Reset
            date_categories = []
            prev_date = record.date

        # Track categories for this date
        date_categories.append(record.category)

        data[record.category]["x"].append(str(record.date))
        data[record.category]["y"].append(record.downloads)
    else:
        # Fill in missing final date with zeros
        for category in all_categories:
            if category not in date_categories:
                data[category]["x"].append(str(record.date))
                data[category]["y"].append(0)
    return data

def get_proportion_data(records):
    data = defaultdict(lambda: {"x": [], "y": [], "text": []})

    date_categories = defaultdict(lambda: 0)
    all_categories = []

    prev_date = records[0].date
    date_csum = 0

    for record in records:
        if record.category not in all_categories:
            all_categories.append(record.category)

    all_categories = sorted(all_categories)
    for category in all_categories:
        data[category]  # set the dict value (keeps it ordered)

    for record in records:
        if record.date != prev_date:

            total = sum(date_categories.values()) / 100
            for category in all_categories:
                data[category]["x"].append(str(record.date))
                value = date_categories[category] / total
                date_csum += value
                data[category]["y"].append(date_csum)
                data[category]["text"].append("{0:.2f}%".format(value) + " = {:,}".format(date_categories[category]))

            # # Fill missing intermediate dates with zeros
            # days_between = (record.date - prev_date).days
            # date_list = [prev_date + datetime.timedelta(days=x) for x in range(1, days_between)]
            #
            # for date in date_list:
            #     for category in all_categories:
            #         data[category]["x"].append(str(date))
            #         data[category]["y"].append(0)

            date_categories = defaultdict(lambda: 0)
            prev_date = record.date
            date_csum = 0

        # Track categories for this date
        date_categories[record.category] = record.downloads
    else:
        # Fill missing intermediate dates with zeros
        total = sum(date_categories.values()) / 100
        for category in all_categories:
            data[category]["x"].append(str(record.date))
            date_csum += date_categories[category]
            data[category]["y"].append(date_csum)
            data[category]["text"].append("{0:.2f}%".format(date_categories[category] / total) + " = {:,}".format(date_categories[category]))

    return data


data_function = {
    "downloads": get_download_data,
    "percentages": get_proportion_data,
}


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
