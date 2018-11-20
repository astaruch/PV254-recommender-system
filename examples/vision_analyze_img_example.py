import io
import os

from lib.vision_analyze_img import analyze_img

file_name = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'mroz_sample_1.jpg')

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

    label_annotations = analyze_img(content)

    print("Received label annotationns for mroz_sample_1.jpg:")
    for label_annotation in label_annotations:
        print(label_annotation)
