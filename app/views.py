import os
from bson import ObjectId
from flask import render_template, Blueprint, request, url_for, redirect, session
from app import db, auth

app_blueprint = Blueprint("app", __name__)

UPLOAD_DEVICE_PHOTO = "app/static/images/devicePhotos"
UPLOAD_BARCODES = "app/static/images/barCodes"
os.makedirs(UPLOAD_DEVICE_PHOTO, exist_ok=True)

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

# @app_blueprint.route("/listujModele", methods = ['POST', 'GET'])
# @auth.login_required()
# def ListModels(*, context):
#
#     if not db.models.find_one():
#         allModels = False
#     else:
#         allModels = list(db.models.find())
#
#         for model in allModels:
#             model["names"] = ""
#             listLength = len(model["specs"]) - 1
#             index = 0
#             for spec in model["specs"]:
#                 if index != listLength:
#                     model["names"] += spec["name"] + ", "
#                     index += 1
#                 else:
#                     model["names"] += spec["name"]
#
#
#
#     if request.method == "POST":
#
#         if request.form.get("infoId"):
#             infoId = request.form.get("infoId")
#             return  redirect(url_for("app.AddModels", infoId = infoId))
#
#         action = request.form.get("action")
#
#         if action == "delete":
#             deleteID = request.form.get("deleteModel")
#             db.models.find_one_and_delete({"_id": ObjectId(deleteID)})
#             return redirect(url_for("app.ListModels"))
#
#         if action == "add":
#             return redirect(url_for("app.AddModels"))
#
#     return render_template("listModels.html", models = allModels ,username = context['user']['name'])
#
# @app_blueprint.route("/dodajModel", methods = ['POST', 'GET'])
# @auth.login_required()
# def AddModels(*, context):
#
#     allTypes = db.specs.find_one({"name": "Typ urządzenia"})
#     allManufacturers = db.specs.find_one({"name": "Producent"})
#     allSpecs = list(db.specs.find({"name": {"$nin": ["Typ urządzenia", "Producent"]}}))
#
#     currentModel = db.models.find_one({"_id": ObjectId(request.args.get("infoId"))})
#
#     if currentModel:
#         existingSpecs = list(currentModel["specs"])
#     else:
#         existingSpecs = []
#
#     if not allTypes:
#         typeList = False
#     else:
#         typeList = allTypes["options"]
#
#     if not allManufacturers:
#         manufacturerList = False
#     else:
#         manufacturerList = allManufacturers["options"]
#
#     if request.method == "POST":
#         data = json.loads(request.form['data'])
#         action = json.loads(request.form['action'])
#         print(data)
#
#         if action["action"] == "update":
#             print(action["id"])
#             db.models.find_one_and_update({"_id": ObjectId(action["id"])}, {"$set": data})
#         elif action["action"] == "create":
#             db.models.insert_one(data)
#
#         return redirect(url_for("app.ListModels"))
#
#     return render_template("addModels.html", types = typeList, manufacturers = manufacturerList, specs = allSpecs, existingSpecs = existingSpecs, modelInfo = currentModel, updateID = request.args.get("infoId") ,username = context['user']['name'])

@app_blueprint.route("/dodajUrządzenie", methods = ['POST', 'GET'])
@auth.login_required()
def AddDevice(*, context):
    allSpecs = list(db.specs.find())

    if request.method == "POST":
        deviceData = request.form.to_dict()

        if deviceData["room"] == "brak":
            print("Wyłapuje on nie ma pokoju!!")

        addedDevice = db.devices.insert_one(deviceData)

        if request.files:
            file = request.files["image"]

            file_ext = file.filename.rsplit(".", 1)[-1].lower()

            filename = "device" + str(addedDevice.inserted_id) + ".png"
            if file_ext in ["jpg", "jpeg", "png", "gif"]:
                save_path = os.path.join(UPLOAD_DEVICE_PHOTO, filename)
            else:
                print("plik niepoprawny")
                return redirect(url_for("app.AddDevice"))

            file.save(save_path)

        return redirect(url_for("app.AddDevice"))

    return render_template("addDevice.html", specs = allSpecs, username = context['user']['name'])

@app_blueprint.route("/edytujUrządzenie", methods = ['POST', 'GET'])
@auth.login_required()
def EditDevice(*, context):
    allSpecs = list(db.specs.find())
    editedDevice = db.devices.find_one({"_id": ObjectId("67ec17b41b81666915348110")})
    deviceSpecs = editedDevice["specs"]
    editedDevice["_id"] = str(editedDevice["_id"])

    if request.method == "POST":
        deviceData = request.form.to_dict()

        if deviceData["room"] == "brak":
            print("Wyłapuje on nie ma pokoju!!")

        addedDevice = db.devices.insert_one(deviceData)

        if request.files:
            file = request.files["image"]
            filename = "device" + str(addedDevice.inserted_id)

            file_ext = file.filename.rsplit(".", 1)[-1].lower()

            if file_ext in ["jpg", "jpeg", "png", "gif"]:
                save_path = os.path.join(UPLOAD_DEVICE_PHOTO, filename + "." + file_ext)
            else:
                print("plik niepoprawny")
                return redirect(url_for("app.EditDevice"))

            file.save(save_path)

        return redirect(url_for("app.EditDevice"))

    return render_template("editDevice.html", specs = allSpecs, deviceSpecs = deviceSpecs, editedDevice = editedDevice ,username = context['user']['name'])

TESTID = "67ebe689a72b651250d0ba44"