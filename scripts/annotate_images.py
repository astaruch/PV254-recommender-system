import argparse
import io
import os
import sqlite3

from lib import database_sql_commands
from lib.vision_analyze_img import analyze_img


class AnnotateImages(object):
    def __init__(self):
        self.options = self.parse_commandline()

    @staticmethod
    def parse_commandline():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--input', type=str, default=None, required=True,
                            help='Folder where images are stored.')
        parser.add_argument('--output', type=str, default='db.sqlite3', required=False,
                            help='Database sqlite3 file where output should be stored.')
        return parser.parse_args()

    def run(self):
        db_conn = sqlite3.connect(self.options.output)
        db_conn.execute(database_sql_commands.CREATE_TABLE_IMAGE_LABEL)

        directory_string = os.path.join(
            os.path.dirname(__file__),
            self.options.input)

        directory = os.fsencode(directory_string)

        for file in os.listdir(directory):
            filename = os.fsdecode(file)

            if filename.endswith(".jpg"):
                image_filename = os.path.join(directory_string, filename)
                print('Annotating image: %s.' % image_filename)

                with io.open(image_filename, 'rb') as image_file:
                    content = image_file.read()

                    label_annotations = analyze_img(content)

                    print("Received label annotationns for %s." % image_filename)
                    for label_annotation in label_annotations:
                        db_conn.execute(
                            'INSERT INTO image_label (`path_prefix`, `filename`, `label`, `score`) VALUES (?, ?, ?, ?)',
                            (directory_string + '/' if not directory_string.endswith('/') else directory_string,
                             filename,
                             label_annotation.description,
                             label_annotation.score))

        db_conn.commit()
        db_conn.close()


if __name__ == '__main__':
    annotate_images = AnnotateImages()
    annotate_images.run()
