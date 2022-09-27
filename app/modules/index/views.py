import json

from pathlib import Path
from flask import Blueprint, redirect, request, render_template, url_for

# from prometheus_client import generate_latest

from app import app
from app.components.utils import apply_metrics

mod = Blueprint("index", __name__, url_prefix="/")

template_dict = {
    "character_name": "Meric",
    "basics": {
        "class": "Blood Hunter",
        "level": "1",
        "class2": "",
        "level2": "",
        "race": "Human",
        "background": "Haunted One",
        "alignment": "Lawful Neutral",
        "progression_type": "Milestone",
        "player_name": "Simon Kvamme-Garshol",
    },
    "ability": {
        "score": {
            "strength": "17",
            "dexterity": "18",
            "constitution": "15",
            "intelligence": "13",
            "wisdom": "13",
            "charisma": "10",
        }
    },
}

skills = {
    "acrobatics": "dexterity",
    "animal_handling": "wisdom",
    "arcana": "intelligence",
    "athletics": "strength",
    "deception": "charisma",
    "history": "intelligence",
    "insight": "wisdom",
    "intimidation": "charisma",
    "investigation": "intelligence",
    "medicine": "wisdom",
    "nature": "intelligence",
    "perception": "wisdom",
    "performance": "charisma",
    "persuasion": "charisma",
    "religion": "intelligence",
    "sleight_of_hand": "dexterity",
    "stealth": "dexterity",
    "survival": "wisdom",
}


@apply_metrics(endpoint="/")
@mod.route("/", methods=["POST", "GET"])
def index():
    app.logger.debug("Request Method: " + request.method)
    sheet = "brandon_fulljames"

    match request.method:
        case "GET":
            populated_data = generate_data(template_dict)

            sheet_query = f"/sheets/{sheet}?data=" + webarg_dict_encode(populated_data)

            return render_template(
                "home.html", sheet_query=sheet_query, data=populated_data
            )

        case "POST":
            app.logger.debug("raw form data\n" + json.dumps(request.form, indent=2))
            data = form_to_dict(request.form)
            app.logger.debug("Character Sheet Data:\n" + json.dumps(data, indent=2))

            populated_data = generate_data(data)

            sheet_query = f"/sheets/{sheet}?data=" + webarg_dict_encode(populated_data)

            return render_template(
                "home.html", sheet_query=sheet_query, data=populated_data
            )


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
    raw_data = request.args.get("data", "")

    if raw_data == "":
        return render_template(f"pre_sheets/{sheet}.html")

    # data = webarg_dict_decode(raw_data, template_dict)

    data = webarg_dict_decode(raw_data)

    app.logger.debug(f"{sheet}:Sheet Data:\n{json.dumps(data, indent=2)}")

    return render_template(f"sheets/{sheet}.html", data=data)


@apply_metrics(endpoint="/metrics")
@mod.route("/metrics")
def metrics():
    return generate_latest()


def add_field(var, val, raw_data):
    """Adds a value in the location var formatted as path-to-value to a dict"""
    
    data = raw_data.copy()
    fields = var.split("-")

    if len(fields) == 1:
        data[var] = val
        return data

    dict_fields = [data]
    for i, field in enumerate(fields):
        if i == len(fields) - 1:
            dict_fields[i][field] = val
            break

        try:
            dict_fields[i][field]
        except:
            dict_fields[i][field] = {}

        dict_fields.append(dict_fields[i][field])
    return data


def form_to_dict(form):
    raw_data = dict(form).copy()
    data = {}

    for key in raw_data:
        data = add_field(key, raw_data[key], data)

    return data


def webarg_dict_encode(dict_data):
    encoded = dict_data.copy()
    encoded = json.dumps(encoded)
    encoded = encoded.replace('"', "]]~~|")
    encoded = encoded.replace(" ", "]]~|~")
    encoded = encoded.replace("+", "]]~||")
    return encoded


def webarg_dict_decode(string_data):
    decoded = string_data
    decoded = decoded.replace("]]~~|", '"')
    decoded = decoded.replace("]]~|~", " ")
    decoded = decoded.replace("]]~||", "+")
    decoded = json.loads(decoded)
    return decoded


def generate_data(raw_data):
    data = raw_data.copy()

    data["basics"]["class_level"] = calc_class_level(data)
    data["proficiency_bonus"] = add_plus(calc_proficiency_bonus(data))

    # modifiers, saving thows, and skills
    for key in raw_data["ability"]["score"]:
        modifier = calc_modifier(data["ability"]["score"][key])
        saving_throw = calc_saving_throw(modifier)

        data = add_field(f"ability-modifier-{key}", add_plus(modifier), data)
        data = add_field(f"saving_throw-{key}", add_plus(saving_throw), data)

        for skill in skills:
            if skills[skill] == key:
                data = add_field(f"skill-{skill}", add_plus(modifier), data)
    return data


def calc_saving_throw(ability_modifier=0):
    try:
        return int(ability_modifier)
    except Exception as e:
        app.logger.warn(
            f'Could not calculate skill with value {ability_modifier}, returning "".\nError:\n{str(e)}'
        )
        return ""


def calc_skill(ability_modifier=0):
    try:
        return int(ability_modifier)
    except Exception as e:
        app.logger.warn(
            f'Could not calculate skill with value {ability_modifier}, returning "".\nError:\n{str(e)}'
        )
        return ""


def calc_modifier(ability_score=0):
    try:
        return int((int(ability_score) - 10) / 2)
    except Exception as e:
        app.logger.warn(
            f'Could not calculate skill with value {ability_score}, returning "".\nError:\n{str(e)}'
        )
        return ""


def calc_class_level(data):
    try:
        if data["basics"]["class2"] != "":
            return f"{data['basics']['class']} {data['basics']['level']} | {data['basics']['class2']} {data['basics']['level2']}"
        if data["basics"]["class"] != "":
            return f"{data['basics']['class']} {data['basics']['level']}"
    except Exception as e:
        app.logger.warn(
            f'Could not calculate class_level with basics class {data["basics"]["class"]} and basics class2 {data["basics"]["class2"]}, returning "".\nError:\n{str(e)}'
        )
        return ""


def calc_proficiency_bonus(data):
    try:
        if data["basics"]["class2"] != "":
            return int(
                (7 + int(data["basics"]["level"]) + int(data["basics"]["level2"])) / 4
            )
        if data["basics"]["class"] != "":
            return int((7 + int(data["basics"]["level"])) / 4)
    except Exception as e:
        app.logger.warn(
            f'Could not calculate proficiency with basics-level {data["basics"]["level"]} and basics-level2 {data["basics"]["level2"]}, returning "".\nError:\n{str(e)}'
        )
        return ""


def add_plus(val):
    try:
        return "+" + str(val) if int(val) >= 0 else str(val)
    except Exception as e:
        app.logger.warn(f'Could not add plus {val}, returning "".\nError:\n{str(e)}')
        return ""
