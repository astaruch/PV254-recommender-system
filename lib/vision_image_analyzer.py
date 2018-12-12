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


def analyze_images(images, max_results = 25):
    MAX_BATCH_SIZE = 16

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    label_detection_feature = {
        'type': vision.enums.Feature.Type.LABEL_DETECTION,
        'max_results': max_results
    }

    accumulated_requests = []
    prepared_batched_requests = []
    for image_content in images:
        image = types.Image(content=image_content)

        # Performs label detection on the image file
        request_features = [label_detection_feature]

        accumulated_requests += [
            {'image': image, 'features': request_features}
        ]

        if len(accumulated_requests) % MAX_BATCH_SIZE == 0:
            prepared_batched_requests += [accumulated_requests]
            accumulated_requests = []

    # Can fit to the last batch if there are 0 batches prepared
    #  or last batch contains free space equal to the length of "accumulated_requests"
    at_least_one_batch_exists = len(prepared_batched_requests) > 0
    if at_least_one_batch_exists:
        can_fit_to_last_batch = len(prepared_batched_requests[-1]) + len(accumulated_requests) <= MAX_BATCH_SIZE
    else:
        can_fit_to_last_batch = True

    if len(accumulated_requests) > 0 and at_least_one_batch_exists and can_fit_to_last_batch:
        prepared_batched_requests[-1] += accumulated_requests
    elif len(accumulated_requests) > 0:
        prepared_batched_requests += [accumulated_requests]

    batched_label_annotations = []
    for prepared_batch_request in prepared_batched_requests:
        batch_response = client.batch_annotate_images(requests=prepared_batch_request)

        for response in batch_response.responses:
            batched_label_annotations += [response.label_annotations]

    return batched_label_annotations


def annotate_images(path_to_directory, callback_is_analyzed, callback_store_labels):
    directory = os.fsencode(path_to_directory)

    images_to_analyze = []
    image_filenames_to_analyze = []

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

                images_to_analyze += [content]
                image_filenames_to_analyze += [image_filename]


    batched_label_annotations = analyze_images(images_to_analyze)

    for image_idx, label_annotations in enumerate(batched_label_annotations):
        filename = image_filenames_to_analyze[image_idx]
        print("Received label annotations for %s." % filename)
        callback_store_labels(filename, label_annotations)
