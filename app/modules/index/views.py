from pathlib import Path
from flask import Blueprint, redirect, request, render_template, url_for
#from prometheus_client import generate_latest

from app import app
from app.components.utils import apply_metrics

mod = Blueprint("index", __name__, url_prefix="/")


@apply_metrics(endpoint="/")
@mod.route("/", methods=["POST", "GET"])
def index():
    app.logger.debug("Request Method: " + request.method)
    sheet = "brandon_fulljames.html"

    # Get Sheet
    # with open(Path("C:\\Users\\lindcjon\\OneDrive - Tietoevry\\Documents\\git\\OpenDnD\\app\\templates\\sheets\\brandon_fulljames.html"), "r") as f:
    #     sheet_html = f.read()

    match request.method:
        case "GET":
            return render_template("home.html", sheet=url_for('static', filename=f"html/sheets/{sheet}"))

        case "POST":
            character_sheet_data = request.form

            app.logger.debug("Character Sheet Data: " + str(character_sheet_data))
            return render_template("home.html", sheet=url_for('static', filename=f"html/sheets/{sheet}"), raw_data=str(character_sheet_data))


@apply_metrics(endpoint="/home")
@mod.route("/home")
def home():
    return redirect(url_for("index.index"))

@apply_metrics(endpoint="/sheets")
@mod.route("/sheets")
def sheets():
    return f"<p>Sheets available:<br>/sheets/brandon_fulljames<p>"


@apply_metrics(endpoint="/sheets/<sheet>")
@mod.route("/sheets/<sheet>")
def sheets_sheet(sheet):
    character_name = request.args.get("character_name", "")
    print(character_name)
    
    return render_template(f"sheets/{sheet}.html", character_name=character_name)

@apply_metrics(endpoint="/metrics")
@mod.route("/metrics")
def metrics():
    return generate_latest()
