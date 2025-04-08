# Import necessary modules
import re
import os
import json

from barcode import Code128
from bson import ObjectId
from flask import render_template, Blueprint, request, url_for, redirect, session
from app import db, auth

# Create a Flask Blueprint for the application routes
app_blueprint = Blueprint("app", __name__)

# Define upload directories for device photos and barcodes
UPLOAD_DEVICE_PHOTO = "app/static/images/devicePhotos"
UPLOAD_BARCODES = "app/static/images/barCodes"
os.makedirs(UPLOAD_DEVICE_PHOTO, exist_ok=True)  # Create directories if they don't exist
os.makedirs(UPLOAD_BARCODES, exist_ok=True)


@app_blueprint.route("/logout")
def Logout():
    """Handle user logout by clearing session and redirecting to Microsoft logout endpoint"""
    session.clear()
    logout_url = (
            "https://login.microsoftonline.com/568e7eed-2f49-457d-b1d5-a31910e72660/oauth2/v2.0/logout"
            "?post_logout_redirect_uri=" + url_for("Home", _external=True)
    )
    return redirect(logout_url)


@app_blueprint.route("/")
@auth.login_required()
def Validate(*, context):
    """
    Validate user access. If user is not in the database and status is not ignored,
    redirect to logout. Otherwise, redirect to home page.
    """
    status = db.users.find_one({"ignore": "False"})

    if status:
        if not db.users.find_one({"address": context['user']['preferred_username']}):
            return redirect(url_for("app.Logout"))

    return redirect(url_for("app.Home"))


@app_blueprint.route("/home")
@auth.login_required()
def Home(*, context):
    """Render the main map page with all rooms"""
    allRooms = db.rooms.find()
    return render_template("map.html", rooms=allRooms, username=context['user']['name'])


@app_blueprint.route("/edytujSpecyfikacje", methods=['POST', 'GET'])
@auth.login_required()
def EditSpecs(*, context):
    """
    Handle specification editing:
    - GET: Display all specifications for editing
    - POST: Process form submissions for adding, editing, or deleting specifications
    """
    allSpecs = db.specs.find()

    if request.method == "POST":
        if request.form.get("delete"):
            # Delete a specification
            db.specs.find_one_and_delete({"_id": ObjectId(request.form.get("delete"))})
            return redirect(url_for("app.EditSpecs"))

        if request.form.get("saveAllSpecs"):
            # Process all specification changes from the form
            for spec in request.form:
                # Handle new specifications
                if spec[:7] == "newName":
                    index = spec[7:]
                    optionsList = request.form.get("newOptions" + index).split(", ")
                    db.specs.insert_one({"name": request.form.get(spec), "options": optionsList})

                # Handle edited specification names
                if spec[:8] == "editName" and request.form.get(spec):
                    editID = spec[8:]
                    db.specs.find_one_and_update(
                        {"_id": ObjectId(editID)},
                        {"$set": {"name": request.form.get(spec)}}
                    )

                # Handle edited specification options
                if spec[:11] == "editOptions":
                    editID = spec[11:]
                    optionsList = request.form.get(spec).split(", ")
                    db.specs.find_one_and_update(
                        {"_id": ObjectId(editID)},
                        {"$set": {"options": optionsList}}
                    )

    # Convert options lists to comma-separated strings for display
    alteredSpecs = list(allSpecs)
    for item in alteredSpecs:
        item["options"] = ", ".join(item["options"])

    return render_template("editSpecs.html", specs=alteredSpecs, username=context['user']['name'])


@app_blueprint.route("/dodajUrządzenie", methods=['POST', 'GET'])
@auth.login_required()
def AddDevice(*, context):
    """
    Handle device addition:
    - GET: Display form with all specifications and rooms
    - POST: Process new device submission with optional image upload
    """
    allSpecs = list(db.specs.find())
    allRooms = list(db.rooms.find())

    if request.method == "POST":
        deviceData = request.form.to_dict()
        deviceData["specs"] = json.loads(deviceData["specs"])

        # Validate required name field
        if deviceData["name"] == "":
            return redirect(url_for("app.AddDevice"))

        # Handle room assignment
        if deviceData["room"] == "brak":
            deviceData["room"] = {"name": "brak"}
        else:
            roomData = db.rooms.find_one({"name": deviceData["room"]}, {"_id": 0})
            deviceData["room"] = roomData

        # Insert new device into database
        addedDevice = db.devices.insert_one(deviceData)

        # Generate barcode if device is not private
        if deviceData["private"] == "False":
            barCodeData = deviceData["name"]
            barCode = Code128(barCodeData)
            barCodePath = os.path.join(UPLOAD_BARCODES, "barcode" + str(addedDevice.inserted_id))
            barCode.save(barCodePath)

        # Handle image upload
        if request.files:
            file = request.files["image"]
            file_ext = file.filename.rsplit(".", 1)[-1].lower()
            filename = "device" + str(addedDevice.inserted_id) + ".png"

            # Validate file extension
            if file_ext in ["jpg", "jpeg", "png", "gif"]:
                save_path = os.path.join(UPLOAD_DEVICE_PHOTO, filename)
            else:
                return redirect(url_for("app.AddDevice"))

            file.save(save_path)

        return redirect(url_for("app.ListRedirect"))

    return render_template("addDevice.html", specs=allSpecs, rooms=allRooms, username=context['user']['name'])


@app_blueprint.route("/edytujUrządzenie", methods=['POST', 'GET'])
@auth.login_required()
def EditDevice(*, context):
    """
    Handle device editing:
    - GET: Display edit form for a specific device
    - POST: Process device updates including image changes
    """
    allRooms = list(db.rooms.find())

    if request.method == "POST":
        # Handle device deletion
        if request.form.get("delete"):
            device_id = request.form["delete"]
            db.devices.find_one_and_delete({"_id": ObjectId(device_id)})

            # Remove associated files
            if os.path.exists(UPLOAD_DEVICE_PHOTO + "/device" + str(device_id) + ".png"):
                os.remove(UPLOAD_DEVICE_PHOTO + "/device" + str(device_id) + ".png")
            if os.path.exists(UPLOAD_BARCODES + "/barcode" + str(device_id) + ".svg"):
                os.remove(UPLOAD_BARCODES + "/barcode" + str(device_id) + ".svg")
            return redirect(url_for("app.ListDevices"))

        # Process device updates
        deviceData = request.form.to_dict()
        deviceData["specs"] = json.loads(deviceData["specs"])
        deviceId = ObjectId(deviceData["_id"])
        deviceData.pop("_id")

        # Handle room assignment
        if deviceData["room"] == "brak":
            deviceData["room"] = {"name": "brak"}
        else:
            roomData = db.rooms.find_one({"name": deviceData["room"]}, {"_id": 0})
            deviceData["room"] = roomData

        # Update device in database
        db.devices.find_one_and_update({"_id": deviceId}, {"$set": deviceData})

        # Handle image update
        if request.files:
            # Remove old image if exists
            if os.path.exists(UPLOAD_DEVICE_PHOTO + "/device" + str(deviceId) + ".png"):
                os.remove(UPLOAD_DEVICE_PHOTO + "/device" + str(deviceId) + ".png")

            file = request.files["image"]
            filename = "device" + str(deviceId) + ".png"
            file_ext = file.filename.rsplit(".", 1)[-1].lower()

            # Validate and save new image
            if file_ext in ["jpg", "jpeg", "png", "gif"]:
                save_path = os.path.join(UPLOAD_DEVICE_PHOTO, filename)
            else:
                return redirect(url_for("app.ListRedirect"))

            file.save(save_path)

        return redirect(url_for("app.ListDevices"))

    # Handle device lookup by name
    if request.args.get("deviceName"):
        deviceName = request.args.get("deviceName")
        allSpecs = list(db.specs.find())
        editedDevice = db.devices.find_one({"name": deviceName})
        if editedDevice:
            deviceSpecs = editedDevice["specs"]
            editedDevice["_id"] = str(editedDevice["_id"])
            return render_template("editDevice.html",
                                   specs=allSpecs,
                                   deviceSpecs=deviceSpecs,
                                   rooms=allRooms,
                                   editedDevice=editedDevice,
                                   username=context['user']['name'])

    # Handle device lookup by ID
    if request.args.get("deviceId"):
        deviceId = request.args.get("deviceId")
        allSpecs = list(db.specs.find())
        editedDevice = db.devices.find_one({"_id": ObjectId(deviceId)})
        if editedDevice:
            deviceSpecs = editedDevice["specs"]
            editedDevice["_id"] = str(editedDevice["_id"])
            return render_template("editDevice.html",
                                   specs=allSpecs,
                                   deviceSpecs=deviceSpecs,
                                   rooms=allRooms,
                                   editedDevice=editedDevice,
                                   username=context['user']['name'])

    return redirect(url_for("app.ListRedirect"))

@app_blueprint.route("/urządzenia", methods=['POST', 'GET'])
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

        # Filter by device name
        if filter_name:
            query["name"] = {"$regex": f".*{re.escape(filter_name)}.*", "$options": "i"}

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

    allSpecs = list(db.specs.find())
    allRooms = list(db.rooms.find())

    return render_template("listDevices.html",
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


@app_blueprint.route("/lista/", methods=['POST', 'GET'])
@app_blueprint.route("/lista/<roomName>", methods=['POST', 'GET'])
def ListRedirect(roomName=None):
    """Redirect to device list, optionally with room filter"""
    return redirect(url_for("app.ListDevices", roomName=roomName))


@app_blueprint.route("/pomieszczenia", methods=['POST', 'GET'])
@auth.login_required()
def RoomList(*, context):
    """
    Display and manage rooms:
    - GET: Show paginated list of rooms
    - POST: Update room keepers
    """
    if request.method == "POST":
        # Update room keepers from form
        for room in request.form:
            id = room[6:]
            room = db.rooms.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": {"keeper": request.form.get(room)}},
                return_document=True
            )

            # Update all devices in this room with new room data
            room_data = dict(room)
            room_data.pop('_id', None)
            db.devices.update_many(
                {"room.name": room["name"]},
                {"$set": {"room": room_data}}
            )
        return redirect(url_for("app.RoomList"))

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 9
    query = {}
    filter_name = request.args.get('filter', '').strip()
    skip = (page - 1) * per_page

    # Apply name filter if provided
    if filter_name:
        query['name'] = {'$regex': f'.*{filter_name}.*', '$options': 'i'}

    # Get paginated rooms
    allRooms = list(db.rooms.find(query).skip(skip).limit(per_page))

    # Calculate pagination details
    total = db.rooms.count_documents(query)
    total_pages = (total + per_page - 1) // per_page

    return render_template("rooms.html",
                           rooms=allRooms,
                           page=page,
                           total_pages=total_pages,
                           username=context['user']['name'])


@app_blueprint.route("/użytkownicy", methods=['POST', 'GET'])
@auth.login_required()
def UserManagement(*, context):
    """
    Manage privileged users:
    - GET: Display user management interface
    - POST: Handle user additions, edits, deletions, and status changes
    """
    if request.method == "POST":
        # Handle user deletion
        if request.form.get("delete"):
            db.users.find_one_and_delete({"_id": ObjectId(request.form.get("delete"))})
            return redirect(url_for("app.UserManagement"))

        if request.form.get("saveAllSpecs"):
            # Process all user management actions
            for action in request.form:
                # Add new user
                if action[:10] == "newAddress":
                    db.users.insert_one({"address": request.form.get(action)})

                # Edit existing user
                if action[:11] == "editAddress" and request.form.get(action):
                    editID = action[11:]
                    db.users.find_one_and_update(
                        {"_id": ObjectId(editID)},
                        {"$set": {"address": request.form.get(action)}}
                    )

            # Update global user status setting
            if request.form.get("status"):
                db.users.find_one_and_update(
                    {"ignore": {"$exists": True, "$ne": None}},
                    {"$set": {"ignore": "True"}}
                )
            else:
                db.users.find_one_and_update(
                    {"ignore": {"$exists": True, "$ne": None}},
                    {"$set": {"ignore": "False"}}
                )

        return redirect(url_for("app.UserManagement"))

    # Get all privileged users except current user
    allPriviledgedUsers = list(db.users.find(
        {"address": {"$exists": True, "$ne": None, "$ne": context['user']['preferred_username']}}
    ))

    # Get current status setting
    status = db.users.find_one({"ignore": {"$exists": True, "$ne": None}})

    # Ensure at least one user exists
    if len(allPriviledgedUsers) < 1:
        db.users.find_one_and_update(
            {"ignore": {"$exists": True, "$ne": None}},
            {"$set": {"ignore": "True"}}
        )

    return render_template("userManagement.html",
                           status=status,
                           users=allPriviledgedUsers,
                           username=context['user']['name'])