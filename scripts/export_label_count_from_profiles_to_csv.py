import argparse
import os
import sqlite3

COUNT_LABELS_FOR_PROFILES = '''
  SELECT count(*), label, path_prefix
  FROM image_label
  WHERE  score >= ?
  GROUP BY label, path_prefix;
'''

class ExportDatabase(object):
    def __init__(self):
        self.options = self.parse_commandline()

    @staticmethod
    def parse_commandline():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--dbfile', type=str, default='db.sqlite3', required=False,
                            help='Path to db.')
        parser.add_argument('--output', type=str, default='export.csv', required=False,
                            help='Path to csv file exported.')
        parser.add_argument('--min_score', type=int, default=0.0, required=False,
                            help='Path to csv file exported.')
        return parser.parse_known_args()[0]

    def run(self):
        db_conn = sqlite3.connect(self.options.dbfile)

        profiles_with_label_counts = db_conn.execute(COUNT_LABELS_FOR_PROFILES, (self.options.min_score,)).fetchall()

        print('Retrieved %s rows with label counts.' % len(profiles_with_label_counts))
        db_conn.close()

        output_filename_string = os.path.join(self.options.output)

        print('Generating output file: %s.' % output_filename_string)
        with open(output_filename_string, 'w') as output_file:
            output_file.write('count, label, path_prefix\n')
            for profile_with_label_counts in profiles_with_label_counts:
              count, label, path_prefix = profile_with_label_counts
              output_file.write('%s, %s, %s\n' %(str(count), str(label), str(path_prefix)))

        print('Done.')

if __name__ == '__main__':
    export_database = ExportDatabase()
    export_database.run()
