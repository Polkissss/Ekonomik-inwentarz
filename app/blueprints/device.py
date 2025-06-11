# Import necessary modules
import json
import re

from app.models.specs import Spec
from app.models.device import Device
from app.models.rooms import Rooms

import app.helpers.device_utils as Utils

from flask import render_template, Blueprint, request, url_for, redirect
from app import auth, db

device_blueprint = Blueprint("device", __name__)

@device_blueprint.route("/dodaj", methods=['POST', 'GET'])
@auth.login_required()
def AddDevice(*, context):
    """
    Handle device addition:
    - GET: Display form with all specifications and rooms
    - POST: Process new device submission with optional image upload
    """
    allSpecs = Spec.Find()
    allRooms = Rooms.Find()

    if request.method == "POST":
        deviceData = request.form.to_dict()
        processedData = Utils.ProcessData(deviceData, context['user']['preferred_username'])

        # Insert new device into database
        addedDevice = Device.Create(processedData)

        if not addedDevice:
            return redirect(url_for("device.ListDevices"))

        # Generate barcode if device is not private
        if processedData["private"] == "False":
            Utils.GenerateBarCode(processedData["ID"], addedDevice.inserted_id)

        # Handle image upload
        if request.files:
            if Utils.SaveDeviceImage(request.files["image"], addedDevice.inserted_id):
                return redirect(url_for("home.Home"))
            else:
                print("error")
                return redirect(url_for("Device.AddDevice"))

        return redirect(url_for("device.ListDevices"))

    return render_template("/device/add.html", specs=allSpecs, rooms=allRooms, username=context['user']['name'])


@device_blueprint.route("/edytuj", methods=['POST', 'GET'])
@auth.login_required()
def EditDevice(*, context):
    """
    Handle device editing:
    - GET: Display edit form for a specific device
    - POST: Process device updates including image changes
    """
    allRooms = list(Rooms.Find())

    if request.method == "POST":
        # Handle device deletion
        if request.form.get("delete"):
            device_id = request.form["delete"]
            Device.DeleteBy_ID(device_id)

            # Remove associated files
            Utils.DeleteFiles(device_id)
            return redirect(url_for("device.ListDevices"))

        # Process device updates
        deviceData = request.form.to_dict()
        deviceId = deviceData["_id"]
        data = Utils.ProcessData(deviceData)

        # Update device in database
        Device.Edit(deviceId, data)


        # Handle image update
        if request.files:
            print("zapisuje plik")
            # Remove old image if exists
            Utils.SaveDeviceImage(request.files["image"], deviceId)
            return redirect(url_for("device.ListDevices"))


        return redirect(url_for("device.ListDevices"))


    # Handle device lookup by ID
    if request.args.get("deviceID"):
        print("szukam")
        deviceID = request.args.get("deviceID")
        editedDevice = Device.FindOne({"ID": deviceID})
        if editedDevice:
            imageExists = Utils.ImageLookup(editedDevice["_id"])
            allSpecs = list(Spec.Find())
            deviceSpecs = editedDevice["specs"]
            editedDevice["_id"] = str(editedDevice["_id"])
            return render_template("/device/edit.html",
                                   specs=allSpecs,
                                   deviceSpecs=deviceSpecs,
                                   rooms=allRooms,
                                   editedDevice=editedDevice,
                                   imageExists=imageExists,
                                   username=context['user']['name'])

    return redirect(url_for("device.ListDevices"))

@device_blueprint.route("/lista", methods=['POST', 'GET'])
@auth.login_required()
def ListDevices(*, context):
    """
    Display paginated list of devices with filtering capabilities:
    - Filter by room name
    - Filter by device name
    - Filter by specifications
    """
    roomName = request.args.get('roomName')

    # TODO: Optimize paghination

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 14
    skip = (page - 1) * per_page

    # Base query
    query = {}

    # Filter by room name from GET parameter
    if roomName:
        query["room.name"] = roomName

    # Handle filter form submission
    if request.method == "POST":
        filter_specs = json.loads(request.form.get("filterSpecs", "{}"))
        filter_name = request.form.get("filterName", "").strip()
        filter_ID = request.form.get("filterID", "").strip()

        # Filter by device name
        if filter_name:
            query["name"] = {"$regex": f".*{re.escape(filter_name)}.*", "$options": "i"}

        if filter_ID:
            query["ID"] = {"$regex": f".*{re.escape(filter_ID)}.*", "$options": "i"}

        # Filter by specifications
        if filter_specs:
            for field, value in filter_specs.items():
                str_value = str(value)
                if field == "Pomieszczenie":
                    query[f"room.name"] = {
                        "$regex": f"^{re.escape(str_value)}$",
                        "$options": "i"
                    }
                else:
                    query[f"specs.{field}"] = {
                        "$regex": f"^{re.escape(str_value)}$",
                        "$options": "i"
                    }

    # Get paginated devices
    allDevices = list(db.devices.find(query).skip(skip).limit(per_page))

    # Calculate pagination details
    total = db.devices.count_documents(query)
    total_pages = (total + per_page - 1) // per_page

    # Convert ObjectId to string for template rendering
    for device in allDevices:
        device["_id"] = str(device["_id"])

    allSpecs = list(Spec.Find())
    allRooms = list(Rooms.Find())

    return render_template("device/list.html",
                           devices=allDevices,
                           page=page,
                           rooms=allRooms,
                           total_pages=total_pages,
                           specs=allSpecs,
                           username=context['user']['name'],
                           current_filters={
                               'roomName': roomName,
                               'filterName': request.form.get("filterName", ""),
                               'filterSpecs': request.form.get("filterSpecs", "{}")
                           })

@device_blueprint.route("/lista/<roomName>", methods=['POST', 'GET'])
def ListRedirect(roomName=None):
    """Redirect to device list, optionally with room filter"""
    return redirect(url_for("device.ListDevices", roomName=roomName))