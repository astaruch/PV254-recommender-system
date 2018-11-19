import os
import io
from vision_analyze_img import analyze_img

file_name = os.path.join(
  os.path.dirname(__file__),
  'mroz_sample_1.jpg')

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
  content = image_file.read()

  analyze_img(content)


