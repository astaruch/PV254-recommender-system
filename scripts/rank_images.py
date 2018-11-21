import argparse
import os
import sqlite3


class RankImages(object):
    def __init__(self):
        self.options = self.parse_commandline()

    @staticmethod
    def parse_commandline():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--library', type=str, default=None, required=True,
                            help='Path to library with annotated images.')
        parser.add_argument('--input', type=str, default=None, required=True,
                            help='Path to annotated image candidates.')
        parser.add_argument('--output', type=str, default='recommendations.html', required=False,
                            help='Output file path.')
        parser.add_argument('--count', type=int, default=15, required=False,
                            help='Count of recommendations.')
        parser.add_argument('--dbfile', type=str, default='database.sqlite3', required=False,
                            help='Database sqlite3 file where output should be stored.')
        return parser.parse_args()

    def run(self):
        db_conn = sqlite3.connect(self.options.dbfile)

        library_data = db_conn.execute(
            'SELECT filename, label, score FROM image_label WHERE path_prefix LIKE ?', ('{}%'.format(self.options.library),)).fetchall()
        candidate_data = db_conn.execute(
            'SELECT filename, label, score FROM image_label WHERE path_prefix LIKE ?', ('{}%'.format(self.options.input),)).fetchall()

        print('Retrieved %s labels for library data.' % len(library_data))
        print('Retrieved %s labels for candidate data.' % len(candidate_data))

        db_conn.close()

        # Do magic here.

        # Prepare best candidates as tuples (filename, score, list of reasons).
        winners = [
            (candidate_data[20][0], 20, ['this matches with that', 'cool pic']),
            (candidate_data[60][0], 50, ['green is greener', 'i like this']),
            (candidate_data[100][0], 10, ['matches with label x and y']),
        ]

        output_filename_string = os.path.join(
            os.path.dirname(__file__),
            self.options.input,
            self.options.output)

        print('Generating output file: %s.' % output_filename_string)
        with open(output_filename_string, 'w') as output_file:
            output_file.write('<head>\n<body>\n</head>\n')

            count = 0
            for (filename, score, reasons) in sorted(winners, key=lambda k: -k[1]):
                if count >= self.options.count:
                    break
                count += 1

                output_file.write('<img src="%s"/>\n' % filename)
                output_file.write('<p>Score: %s<br />\n' % score)
                output_file.write('Reasons:</p><ul>\n')
                for reason in reasons:
                    output_file.write('<li>%s</li>\n' % reason)
                output_file.write('</ul><br /><br /><br />\n')

            output_file.write('</body>\n')

        print('Done.')

if __name__ == '__main__':
    rank_images = RankImages()
    rank_images.run()
