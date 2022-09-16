from flask import Blueprint, redirect, request, render_template, url_for
#from prometheus_client import generate_latest

from app import app
from app.components.utils import apply_metrics

mod = Blueprint("index", __name__, url_prefix="/")


@apply_metrics(endpoint="/home")
@mod.route("/", methods=["POST", "GET"])
def index():
    app.logger.debug("Request Method: " + request.method)
    match request.method:
        case "GET":
            return render_template("home.html")

        case "POST":
            character_sheet_data = request.form

            app.logger.debug("Character Sheet Data: " + str(character_sheet_data))
            return render_template("home.html", raw_data = str(character_sheet_data))


@apply_metrics(endpoint="/")
@mod.route("/home")
def home():
    return redirect(url_for("index.index"))


@apply_metrics(endpoint="/metrics")
@mod.route("/metrics")
def metrics():
    return generate_latest()
