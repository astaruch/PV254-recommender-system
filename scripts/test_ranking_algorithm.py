import argparse
import os
import random
import sqlite3
from lib import image_ranker


class TestRankingAlgorithm(object):
    def __init__(self):
        self.options = self.parse_commandline()

    @staticmethod
    def parse_commandline():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--library', type=str, default=None, required=True,
                            help='Path to library with annotated images.')
        parser.add_argument('--candidates', type=str, default=None, required=True,
                            help='Path to annotated image candidates.')
        parser.add_argument('--dbfile', type=str, default='db.sqlite3', required=False,
                            help='Database sqlite3 file where output should be stored.')
        parser.add_argument('--positive', type=float, default=1.033, required=False,
                            help='Coefficient to fine-tune the scoring for matching labels.')
        parser.add_argument('--negative', type=float, default=1.44, required=False,
                            help='Coefficient to fine-tune the scoring for non-matching labels.')
        parser.add_argument('--mix-coef', type=float, default=0.1, required=False,
                            help='How many percent from IG profile should be mixed into candidates. (0.0-1.0)')
        parser.add_argument('--iterations', type=int, default=1, required=False,
                            help='Number of iterations.')
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

        for iteration_number in range(self.options.iterations):
            iteration_library_data = dict()
            for filename, label, score in library_data:
                if filename not in iteration_library_data:
                    iteration_library_data[filename] = []
                iteration_library_data[filename].append((label, score))

            iteration_candidate_data = dict()
            for filename, label, score in candidate_data:
                if filename not in iteration_candidate_data:
                    iteration_candidate_data[filename] = []
                    iteration_candidate_data[filename].append((label, score))

            candidates_count_to_mix = int(len(iteration_library_data) * self.options.mix_coef)
            if candidates_count_to_mix > len(iteration_library_data):
                print('Mix coefficient is higher than 1.0!')
                continue

            print('Mixing %s images into %s candidate images.' % (candidates_count_to_mix, len(iteration_candidate_data)))

            mixed_candidates_from_library = []
            for i in range(candidates_count_to_mix):
                key = random.choice(list(iteration_library_data))
                value = iteration_library_data.pop(key)

                mixed_candidates_from_library.append(key)
                iteration_candidate_data[key] = value


            winners = image_ranker.rank_images_mroz(
                [(k, x[0], x[1]) for k, v in iteration_library_data.items() for x in v],
                [(k, x[0], x[1]) for k, v in iteration_candidate_data.items() for x in v],
                matching_coefficient,
                absent_coefficient)

            score_sum = 0
            for filename, score, reasons in winners:
                if filename in mixed_candidates_from_library:
                    score_sum += score
            print('Score sum for iteration %s is %s.' % (iteration_number, score_sum))

            output_filename_string = os.path.join('recommendations-%s.html' % iteration_number)

            print('Generating output file: %s.' % output_filename_string)
            with open(output_filename_string, 'w') as output_file:
                output_file.write('<head>\n<body>\n</head>\n')

                for (filename, score, reasons) in sorted(winners, key=lambda k: -k[1]):

                    if filename in mixed_candidates_from_library or filename in iteration_library_data:
                        output_file.write('<img src="%s%s"/>\n' % (self.options.library, filename))
                    else:
                        output_file.write('<img src="%s%s"/>\n' % (self.options.candidates, filename))
                    output_file.write('<p>Score: %s<br />\n' % score)
                    output_file.write('Reasons:</p><ul>\n')
                    for reason in reasons:
                        output_file.write('<li>%s</li>\n' % reason)
                    output_file.write('</ul><br /><br /><br />\n')

                output_file.write('</body>\n')
            print('Iteration %s finished.' % iteration_number)

        print('Done.')


if __name__ == '__main__':
    test_ranking_algorithm = TestRankingAlgorithm()
    test_ranking_algorithm.run()
