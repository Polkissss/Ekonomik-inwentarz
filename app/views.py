import re
import os
import json
from lib2to3.fixes.fix_input import context

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

@app_blueprint.route("/dodajUrządzenie", methods = ['POST', 'GET'])
@auth.login_required()
def AddDevice(*, context):
    allSpecs = list(db.specs.find())

    if request.method == "POST":
        deviceData = request.form.to_dict()
        deviceData["specs"] = json.loads(deviceData["specs"])

        if deviceData["room"] == "brak":
            deviceData["room"] = {"name": "brak"}

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

    if request.method == "POST":

        if request.form.get("delete"):
            db.devices.find_one_and_delete({"_id": ObjectId(request.form["delete"])})
            if os.path.exists(UPLOAD_DEVICE_PHOTO + "/device" + str(request.form["delete"]) + ".png"):
                os.remove(UPLOAD_DEVICE_PHOTO + "/device" + str(request.form["delete"]) + ".png")
            return redirect(url_for("app.ListDevices"))

        deviceData = request.form.to_dict()
        deviceData["specs"] = json.loads(deviceData["specs"])
        deviceId = ObjectId(deviceData["_id"])
        deviceData.pop("_id")

        if deviceData["room"] == "brak":
            deviceData["room"] = {"name": "brak"}

        db.devices.find_one_and_update({"_id": deviceId}, {"$set": deviceData})

        if request.files:
            if os.path.exists(UPLOAD_DEVICE_PHOTO + "/device" + str(deviceId) + ".png"):
                os.remove(UPLOAD_DEVICE_PHOTO + "/device" + str(deviceId) + ".png")

            file = request.files["image"]
            filename = "device" + str(deviceId) + ".png"

            file_ext = file.filename.rsplit(".", 1)[-1].lower()

            if file_ext in ["jpg", "jpeg", "png", "gif"]:
                save_path = os.path.join(UPLOAD_DEVICE_PHOTO, filename)
            else:
                print("plik niepoprawny")
                return redirect(url_for("app.EditDevice"))

            file.save(save_path)

        return redirect(url_for("app.EditDevice"))

    if request.args.get("deviceId"):
        deviceId = request.args.get("deviceId")
        allSpecs = list(db.specs.find())
        editedDevice = db.devices.find_one({"_id": ObjectId(deviceId)})
        deviceSpecs = editedDevice["specs"]
        editedDevice["_id"] = str(editedDevice["_id"])
        if editedDevice:
            return render_template("editDevice.html", specs = allSpecs, deviceSpecs = deviceSpecs, editedDevice = editedDevice ,username = context['user']['name'])
    return redirect(url_for("app.ListRedirect"))

TESTID = "67ebe689a72b651250d0ba44"

@app_blueprint.route("/urządzenia", methods = ['POST', 'GET'])
@auth.login_required()
def ListDevices(*, context):
    roomName = request.args.get('roomName')

    # Pobierz parametry paginacji
    page = request.args.get('page', 1, type=int)
    per_page = 14
    skip = (page - 1) * per_page

    # Budujemy query
    query = {}

    # Filtracja po nazwie pokoju (z GET)
    if roomName:
        query["room.name"] = roomName

    # Filtracja z formularza POST
    if request.method == "POST":
        filter_specs = json.loads(request.form.get("filterSpecs", "{}"))
        filter_name = request.form.get("filterName", "").strip()

        # Filtrowanie po nazwie urządzenia
        if filter_name:
            query["name"] = {"$regex": f".*{re.escape(filter_name)}.*", "$options": "i"}

        # Filtrowanie po specyfikacjach
        if filter_specs:
            for field, value in filter_specs.items():
                str_value = str(value)
                query[f"specs.{field}"] = {
                    "$regex": f"^{re.escape(str_value)}$",
                    "$options": "i"
                }

    # Pobierz urządzenia z uwzględnieniem wszystkich filtrów
    allDevices = list(db.devices.find(query).skip(skip).limit(per_page))

    # Oblicz całkowitą liczbę dokumentów Z UWZGLĘDNIENIEM FILTRÓW
    total = db.devices.count_documents(query)
    total_pages = (total + per_page - 1) // per_page

    # Konwersja ObjectId na string
    for device in allDevices:
        device["_id"] = str(device["_id"])

    allSpecs = list(db.specs.find())

    return render_template("listDevices.html",
                           devices=allDevices,
                           page=page,
                           total_pages=total_pages,
                           specs=allSpecs,
                           username=context['user']['name'],
                           current_filters={
                               'roomName': roomName,
                               'filterName': request.form.get("filterName", ""),
                               'filterSpecs': request.form.get("filterSpecs", "{}")
                           })

@app_blueprint.route("/lista/", methods = ['POST', 'GET'])
@app_blueprint.route("/lista/<roomName>", methods = ['POST', 'GET'])
def ListRedirect(roomName=None):
    return redirect(url_for("app.ListDevices", roomName=roomName))