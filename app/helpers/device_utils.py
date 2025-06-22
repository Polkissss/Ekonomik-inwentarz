import json
import os
from  datetime import datetime

from barcode import Code128

# Define upload directories for device photos and barcodes
UPLOAD_DEVICE_PHOTO = "app/static/images/device_photos"
UPLOAD_BARCODES = "app/static/images/bar_codes"
os.makedirs(UPLOAD_DEVICE_PHOTO, exist_ok=True)  # Create directories if they don't exist
os.makedirs(UPLOAD_BARCODES, exist_ok=True)

def ProcessData(data, user=None):
    from app.models.rooms import Rooms
    if "_id" in data:
        data.pop("_id")

    data["specs"] = json.loads(data["specs"])

    if data["room"] == "brak":
        data["room"] = {"name": "brak"}
    else:
        roomData = Rooms.FindOne({"name": data["room"]}, {"_id": 0})
        data["room"] = roomData

    if user:
        data["last_user"] = user

    data["last_update"] = datetime.now()

    return data

def GenerateBarCode(value, id):
    barCode = Code128(value)
    barCodePath = os.path.join(UPLOAD_BARCODES, "barcode" + str(id))
    barCode.save(barCodePath)

def SaveDeviceImage(file, id):
    if os.path.exists(UPLOAD_DEVICE_PHOTO + "/device" + str(id) + ".png"):
        os.remove(UPLOAD_DEVICE_PHOTO + "/device" + str(id) + ".png")

    file_ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = "device" + str(id) + ".png"

    # Validate file extension
    if file_ext in ["jpg", "jpeg", "png", "gif"]:
        save_path = os.path.join(UPLOAD_DEVICE_PHOTO, filename)
    else:
        return False

    file.save(save_path)
    return True

def DeleteFiles(device_id):
    if os.path.exists(UPLOAD_DEVICE_PHOTO + "/device" + str(device_id) + ".png"):
        os.remove(UPLOAD_DEVICE_PHOTO + "/device" + str(device_id) + ".png")
    if os.path.exists(UPLOAD_BARCODES + "/barcode" + str(device_id) + ".svg"):
        os.remove(UPLOAD_BARCODES + "/barcode" + str(device_id) + ".svg")

def ImageLookup(id):
    if os.path.exists(UPLOAD_DEVICE_PHOTO + "/device" + str(id) + ".png"):
        return True
    else:
        return False