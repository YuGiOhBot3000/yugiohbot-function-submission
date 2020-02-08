import io
import os
import tempfile
import uuid
from datetime import datetime

from google.cloud import firestore
from google.cloud import storage
from google.cloud import vision
from werkzeug.utils import secure_filename

# Project ID is determined by the GCLOUD_PROJECT environment variable
db = firestore.Client()


# Helper function that computes the filepath to save files to
def get_file_path(filename):
    # Note: tempfile.gettempdir() points to an in-memory file system
    # on GCF. Thus, any files in it must fit in the instance's memory.
    file_name = secure_filename(filename)
    return os.path.join(tempfile.gettempdir(), file_name)


def upload_card(file, storage_client):
    bucket_name = "yugiohbot-images"

    file_uuid = str(uuid.uuid4())
    name, extension = os.path.splitext(file)
    name = name.replace("/tmp/", "")

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob('submissions/' + name + '_' + file_uuid + extension)
    with open(file, 'rb') as card_file:
        blob.upload_from_file(card_file)
    print("File {} uploaded.".format(file))


def detect_safe_search(path):
    """Detects unsafe features in the file."""

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.safe_search_detection(image=image)
    safe = response.safe_search_annotation

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    print('Safe search:')

    print('adult: {}'.format(likelihood_name[safe.adult]))
    print('medical: {}'.format(likelihood_name[safe.medical]))
    print('spoofed: {}'.format(likelihood_name[safe.spoof]))
    print('violence: {}'.format(likelihood_name[safe.violence]))
    print('racy: {}'.format(likelihood_name[safe.racy]))

    adult = likelihood_name[safe.adult]
    if adult == 'VERY_LIKELY' or adult == 'LIKELY' or adult == 'POSSIBLE':
        return False
    else:
        return True


def save_to_firestore(title, effect):
    date = datetime.now().strftime("%d-%m-%Y-%H:%M:%S+%f")

    if title != "":
        title_ref = db.collection(u'submissions').document(u'titles')
        title_ref.update({
            date: title
        })
        print("Added title to database: {}".format(title))

    if effect != "":
        effect_ref = db.collection(u'submissions').document(u'effects')
        effect_ref.update({
            date: effect
        })
        print("Added effect to database: {}".format(effect))


def function(request):
    """ Parses a 'multipart/form-data' upload request
    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a
         Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """

    # Allows POST requests from any origin with any
    # header and caches preflight response for an 3600s
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Max-Age': '3600'
    }

    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        return '', 204, headers

    data = request.form.to_dict()
    # process_fields(data)

    # This code will process each file uploaded
    files = request.files.to_dict()
    process_files(files)

    # Clear temporary directory
    for file_name in files:
        file_path = get_file_path(file_name)
        os.remove(file_path)

    return "Done", 200, headers


def process_fields(data):
    # This code will process each non-file field in the form
    fields = {}
    for field in data:
        fields[field] = data[field]
        print('Processed field: %s' % field)

    if "title" in fields or "effect" in fields:
        save_to_firestore(fields.get("title", ""), fields.get("effect", ""))


def process_files(files):
    storage_client = storage.Client()
    for file_name, file in files.items():
        path = get_file_path(file_name)
        file.save(path)

        # Only upload if SafeSearch thinks it's safe.
        if detect_safe_search(path):
            upload_card(path, storage_client)
        print('Processed file: %s' % file_name)
