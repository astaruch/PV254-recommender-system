import argparse
import os
import sqlite3

from lib import database_sql_commands
from lib import vision_image_analyzer


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

        directory_string = os.path.join(self.options.input)
        path_prefix = directory_string + '/' if not directory_string.endswith('/') else directory_string

        def callback_is_analyzed(filename):
            return db_conn.execute(
                'SELECT COUNT(*) FROM image_label WHERE path_prefix = ? AND filename = ?',
                (path_prefix, filename)).fetchone()[0] > 0

        def callback_store_labels(filename, label_annotations):
            for label_annotation in label_annotations:
                db_conn.execute(
                    'INSERT INTO image_label (`path_prefix`, `filename`, `label`, `score`) VALUES (?, ?, ?, ?)',
                    (path_prefix,
                     filename,
                     label_annotation.description,
                     label_annotation.score))

        vision_image_analyzer.annotate_images(directory_string, callback_is_analyzed, callback_store_labels)

        db_conn.commit()
        db_conn.close()


if __name__ == '__main__':
    annotate_images = AnnotateImages()
    annotate_images.run()
