import argparse
import os
import sqlite3
from lib import image_ranker


class RankImages(object):
    def __init__(self):
        self.options = self.parse_commandline()

    @staticmethod
    def parse_commandline():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--library', type=str, default=None, required=True,
                            help='Path to library with annotated images.')
        parser.add_argument('--candidates', type=str, default=None, required=True,
                            help='Path to annotated image candidates.')
        parser.add_argument('--output', type=str,
                            default='recommendations.html', required=False,
                            help='Output file path.')
        parser.add_argument('--count', type=int, default=7, required=False,
                            help='Count of recommendations.')
        parser.add_argument('--dbfile', type=str, default='db.sqlite3',
                            required=False,
                            help='Database sqlite3 file where output should be\
                            stored.')
        parser.add_argument('--positive', type=float, default=1.033,
                            required=False,
                            help='Coefficient to fine-tune the scoring for \
                            matching labels.')
        parser.add_argument('--negative', type=float, default=1.44,
                            required=False,
                            help='Coefficient to fine-tune the scoring for \
                            non-matching labels.')
        parser.add_argument('--algorithm', type=str,  default=None,
                            required=True,
                            help='Choose the ranking algorithm.',
                            choices=['mroz', 'naive', 'random', 'galajdator'])
        return parser.parse_args()

    def run(self):
        db_conn = sqlite3.connect(self.options.dbfile)

        library_data = db_conn.execute(
            'SELECT filename, label, score FROM image_label WHERE path_prefix LIKE ?', ('{}%'.format(self.options.library),)).fetchall()
        candidate_data = db_conn.execute(
            'SELECT filename, label, score FROM image_label WHERE path_prefix LIKE ?', ('{}%'.format(self.options.candidates),)).fetchall()

        print('Retrieved %s labels for library data.' % len(library_data))
        print('Retrieved %s labels for candidate data.' % len(candidate_data))

        db_conn.close()

        matching_coefficient = self.options.positive
        absent_coefficient = self.options.negative
        ranking_algorithm = self.options.algorithm

        if ranking_algorithm == 'mroz':
            winners = image_ranker.rank_images_mroz(library_data,
                candidate_data, matching_coefficient, absent_coefficient)
        elif ranking_algorithm == 'naive':
            winners = image_ranker.rank_images_naive(library_data,
                candidate_data)
        elif ranking_algorithm == 'random':
            winners = image_ranker.rank_images_random(candidate_data)
        elif ranking_algorithm == "galajdator":
            winners = image_ranker.rank_images_galajdator(library_data, candidate_data, 5)
        else:
            raise("error: unexpected algorithm")

        output_filename_string = os.path.join(
            self.options.candidates,
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
                if reasons:
                    output_file.write('Reasons:</p><ul>\n')
                    for reason in reasons:
                        output_file.write('<li>%s</li>\n' % reason)
                    output_file.write('</ul>')
                output_file.write('<br /><br /><br />\n')

            output_file.write('</body>\n')

        print('Done.')

if __name__ == '__main__':
    rank_images = RankImages()
    rank_images.run()
