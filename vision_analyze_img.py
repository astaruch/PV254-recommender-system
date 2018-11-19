from __future__ import print_function

import io
import os
import sys

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types


if not "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
  print('Warning: You need to set "GOOGLE_APPLICATION_CREDENTIALS" in order to use Cloud Vision API.', file = sys.stderr)

def analyze_img(image_content):
  # Instantiates a client
  client = vision.ImageAnnotatorClient()

  image = types.Image(content=image_content)

  # Performs label detection on the image file
  response = client.label_detection(image=image)
  labels = response.label_annotations

  print('Labels:')
  for label in labels:
    print(label.description)

  return labels
