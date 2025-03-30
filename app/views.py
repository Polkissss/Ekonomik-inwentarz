from pickletools import read_decimalnl_long

from bson import ObjectId
from flask import render_template, Blueprint, request, url_for, redirect, session
from app import db, auth

app_blueprint = Blueprint("app", __name__)

@app_blueprint.route("/redirect")
def Redirect():
    return redirect(url_for("app.Home"))

@app_blueprint.route("/")
@auth.login_required()
def Home(*, context):
    return render_template("map.html", username = context['user']['name'])


@app_blueprint.route("/edytujSpecyfikacje", methods = ['POST', 'GET'])
@auth.login_required()
def EditSpecs(*, context):

    allSpecs = db.specs.find()

    if request.method == "POST":
        if request.form.get("deleteSpec"):
            db.specs.find_one_and_delete({"_id": ObjectId(request.form.get("deleteSpec"))})
            return redirect(url_for("app.EditSpecs"))

        if request.form.get("saveAllSpecs"):
            for spec in request.form:

                if spec[:7] == "newName":
                    index = spec[7:]
                    optionsList = request.form.get("newOptions" + index).split(", ")
                    db.specs.insert_one({"name": request.form.get(spec), "options": optionsList})

                if spec[:8] == "editName" and request.form.get(spec):
                    editID = spec[8:]
                    db.specs.find_one_and_update({"_id": ObjectId(editID)},
                                                 {"$set":
                                                      {"name": request.form.get(spec)}})

                if spec[:11] == "editOptions":
                    editID = spec[11:]
                    optionsList = request.form.get(spec).split(", ")
                    print("Zedytuj: " + editID)
                    db.specs.find_one_and_update({"_id": ObjectId(editID)},
                                                 {"$set":
                                                    {"options": optionsList}})

    alteredSpecs = list(allSpecs)

    for item in alteredSpecs:
        item["options"] = ", ".join(item["options"])

    return render_template("editSpecs.html", specs = alteredSpecs, username = context['user']['name'])

@app_blueprint.route("/listujModele", methods = ['POST', 'GET'])
@auth.login_required()
def listModels(*, context):
    allModels = {"test": "test"}

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            return redirect(url_for("app.addModels"))

    return render_template("listModels.html", models = allModels ,username = context['user']['name'])

@app_blueprint.route("/dodajModel", methods = ['POST', 'GET'])
@auth.login_required()
def addModels(*, context):
    allTypes = db.specs.find_one({"name": "Typ urządzenia"})
    allModels = {"test": "test"}
    return render_template("editModels.html", types = allTypes["options"] ,models = allModels ,username = context['user']['name'])
