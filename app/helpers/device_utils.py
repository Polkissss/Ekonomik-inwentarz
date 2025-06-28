import json
import os

import barcode
from datetime import datetime

Code128 = barcode.get_barcode_class('code128')

# Define upload directories for device photos and barcodes
UPLOAD_DEVICE_PHOTO = "device_photos/"
UPLOAD_BARCODES = "barcodes/"
os.makedirs("app/static/images/barcodes", exist_ok=True)

def ProcessData(data, user=None):
    from app.models.rooms import Rooms
    if "_id" in data:
        data.pop("_id")

    data["specs"] = json.loads(data["specs"])

    roomData = Rooms.FindOne({"name": data["room"]}, {"_id": 0})
    data["room"] = roomData

    if user:
        data["last_user"] = user

    data["last_update"] = datetime.now()

    return data

def GenerateBarCode(value, id):
    from app import s3
    barCode = Code128(value)
    barCodePath = os.path.join("app/static/images/barcodes", "barcode" + str(id))
    barCode.save(barCodePath)

    with open(f"app/static/images/barcodes/barcode{str(id)}.svg", "rb") as file:
        s3.upload_fileobj(file, "ekonomik-inwentarz", f"{UPLOAD_BARCODES}barcode{id}.svg")

def SaveDeviceImage(file, id):
    from app import s3
    file_path = UPLOAD_DEVICE_PHOTO + "/device" + str(id) + ".png"

    s3.delete_object(Bucket="ekonomik-inwentarz", Key=file_path)

    if os.path.exists(file_path):
        s3.delete_object(Bucket="ekonomik-inwentarz", Key=file_path)

    file_ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = "device" + str(id) + ".png"

    # Validate file extension
    if file_ext in ["jpg", "jpeg", "png", "gif"]:
        save_path = UPLOAD_DEVICE_PHOTO + filename
    else:
        return False

    s3.upload_fileobj(file, "ekonomik-inwentarz", save_path)
    return True

def DeleteFiles(device_id):
    from app import s3
    s3.delete_object(Bucket="ekonomik-inwentarz", Key=f"{UPLOAD_DEVICE_PHOTO}device{str(device_id)}.png")
    s3.delete_object(Bucket="ekonomik-inwentarz", Key=f"{UPLOAD_BARCODES}barcode{str(device_id)}.svg")

    if os.path.exists("app/static/images/barcodes" + "/barcode" + str(device_id) + ".svg"):
        os.remove("app/static/images/barcodes" + "/barcode" + str(device_id) + ".svg")

def ImageLookup(id):
    if os.path.exists(UPLOAD_DEVICE_PHOTO + "/device" + str(id) + ".png"):
        return True
    else:
        return False