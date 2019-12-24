import os
import tempfile

from werkzeug.utils import secure_filename
from google.cloud import storage


# Helper function that computes the filepath to save files to
def get_file_path(filename):
    # Note: tempfile.gettempdir() points to an in-memory file system
    # on GCF. Thus, any files in it must fit in the instance's memory.
    file_name = secure_filename(filename)
    return os.path.join(tempfile.gettempdir(), file_name)


def upload_card(file, storage_client):
    bucket_name = "yugiohbot-images"
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob('submissions/' + file)
    with open(file, 'rb') as card_file:
        blob.upload_from_file(card_file)
    print("File {} uploaded.".format(file))


def function(request):
    """ Parses a 'multipart/form-data' upload request
    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a
         Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """

    # This code will process each non-file field in the form
    fields = {}
    data = request.form.to_dict()
    for field in data:
        fields[field] = data[field]
        print('Processed field: %s' % field)

    storage_client = storage.Client()

    # This code will process each file uploaded
    files = request.files.to_dict()
    for file_name, file in files.items():
        path = get_file_path(file_name)
        file.save(path)
        upload_card(path, storage_client)
        print('Processed file: %s' % file_name)

    # Clear temporary directory
    for file_name in files:
        file_path = get_file_path(file_name)
        os.remove(file_path)

    return "Done", 200
