import base64
import datetime
import requests

from firebase_admin import storage


def readFirebase(path):
    try:
        bucket = storage.bucket()
        imageBlob = bucket.blob(path)
        imageUrl = imageBlob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
        imageRequest = requests.get(imageUrl)
        imageBytes = imageRequest.content
        return base64.encodebytes(imageBytes).decode('ascii')
    except Exception as ex:
        return None


def uploadFirebase(path, image):
    try:
        bucket = storage.bucket()
        imageBlob = bucket.blob(path)
        imageBlob.upload_from_file(image, content_type='image/{}'.format(type))
    except Exception as ex:
        return None


def deleteFirebase(path):
    try:
        bucket = storage.bucket()
        imageBlob = bucket.blob(path)
        imageBlob.delete()
    except Exception as ex:
        return None
