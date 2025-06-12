# Import necessary modules
import json
import re

from werkzeug.routing import ValidationError

from app.models.specs import Spec
from app.models.device import Device
from app.models.rooms import Rooms

import app.helpers.device_utils as Utils

from flask import render_template, Blueprint, request, url_for, redirect, flash
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
        try:
            addedDevice = Device.Create(processedData)
        except ValidationError as e:
            flash(str(e), "danger")
            return redirect(url_for("device.AddDevice"))

        # Generate barcode if device is not private
        if processedData["private"] == "False":
            Utils.GenerateBarCode(processedData["ID"], addedDevice.inserted_id)
        else:
            Utils.GenerateBarCode("PRYWATNE", addedDevice.inserted_id)

        # Handle image upload
        if request.files:
            if Utils.SaveDeviceImage(request.files["image"], addedDevice.inserted_id):
                return redirect(url_for("device.ListDevices"))
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
        try:
            Device.Edit(deviceId, data)
        except ValidationError as e:
            flash(str(e), "danger")
            return redirect(url_for("device.EditDevice") + f"?&deviceID={data["ID"]}")


        # Handle image update
        if request.files:
            print("zapisuje plik")
            # Remove old image if exists
            Utils.SaveDeviceImage(request.files["image"], deviceId)
            return redirect(url_for("device.ListDevices"))


        return redirect(url_for("device.ListDevices"))


    # Handle device lookup by ID
    if request.args.get("deviceID"):
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

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    perPage = 9
    skip = (page - 1) * perPage

    # Base query
    query = {}

    # Filter by room name from GET parameter
    if roomName:
        query["room.name"] = roomName

    # Handle filter form submission
    if request.method == "GET":
        filterSpecs = json.loads(request.args.get("filterSpecs", "{}"))
        filterName = request.args.get("filterName", "").strip()
        filterID = request.args.get("filterID", "").strip()

        # Filter by device name
        if filterName:
            query["name"] = {"$regex": f".*{re.escape(filterName)}.*", "$options": "i"}

        if filterID:
            query["ID"] = {"$regex": f".*{re.escape(filterID)}.*", "$options": "i"}

        # Filter by specifications
        if filterSpecs:
            for field, value in filterSpecs.items():
                strValue = str(value)
                if field == "Pomieszczenie":
                    query[f"room.name"] = {
                        "$regex": f"^{re.escape(strValue)}$",
                        "$options": "i"
                    }
                else:
                    query[f"specs.{field}"] = {
                        "$regex": f"^{re.escape(strValue)}$",
                        "$options": "i"
                    }

    # Get paginated devices
    allDevices = list(Device.Find(query).skip(skip).limit(perPage))

    # Calculate pagination details
    total = Device.TotalDocuments(query)
    total_pages = (total + perPage - 1) // perPage

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
                               'filterName': request.args.get("filterName", ""),
                               'filterID': request.args.get("filterID", ""),
                               'filterSpecs': request.args.get("filterSpecs", "{}")
                           })

@device_blueprint.route("/lista/<roomName>", methods=['POST', 'GET'])
def ListRedirect(roomName=None):
    """Redirect to device list, optionally with room filter"""
    return redirect(url_for("device.ListDevices", roomName=roomName))