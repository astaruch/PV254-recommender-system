from __future__ import print_function

import io
import os
import sys
import json

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

if "GOOGLE_API_JSON_FILE" in os.environ:
    print("Info: Creating 'access.json' file for Cloud Vision API.")
    json_data = json.loads(os.environ["GOOGLE_API_JSON_FILE"])
    with open('access.json', 'w') as json_output_file:
        json.dump(json_data, json_output_file)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
            os.environ['PYTHONPATH'],
            'access.json'
        )
elif not "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    print("""Warning: You need to set "GOOGLE_APPLICATION_CREDENTIALS" in order to use Cloud Vision API.
    Using default value <PATH_TO_FILE_DIR>/.secrets/access.json
  """, file=sys.stderr)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        os.environ['PYTHONPATH'],
        '.secrets',
        'access.json'
    )


def analyze_img(image_content):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    image = types.Image(content=image_content)

    # Performs label detection on the image file
    label_detection_feature = {
        'type': vision.enums.Feature.Type.LABEL_DETECTION, 'max_results': 25}
    request_features = [label_detection_feature]
    response = client.annotate_image({'image': image, 'features': request_features})

    return response.label_annotations


def annotate_images(path_to_directory, callback_is_analyzed, callback_store_labels):
    directory = os.fsencode(path_to_directory)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if filename.endswith(".jpg"):
            image_filename = os.path.join(path_to_directory, filename)
            print('Annotating image: %s.' % image_filename)

            if callback_is_analyzed(filename):
                print('Image is already analyzed.')
                continue

            with io.open(image_filename, 'rb') as image_file:
                content = image_file.read()

                label_annotations = analyze_img(content)

                print("Received label annotationns for %s." % image_filename)
                callback_store_labels(filename, label_annotations)
