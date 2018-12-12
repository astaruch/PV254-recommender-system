import argparse
import os
import random
import sqlite3
from lib import image_ranker
from lib.lexvec_model import lexvec_model

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

        # print('Retrieved %s labels for library data.' % len(library_data))
        # print('Retrieved %s labels for candidate data.' % len(candidate_data))
        print("score_sum,")
        db_conn.close()
        # model = lexvec_model.Model('./lib/lexvec_model/lexvec_model.bin')

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

            # print('Mixing %s images into %s candidate images.' % (candidates_count_to_mix, len(iteration_candidate_data)))

            mixed_candidates_from_library = []
            for i in range(candidates_count_to_mix):
                key = random.choice(list(iteration_library_data))
                value = iteration_library_data.pop(key)

                mixed_candidates_from_library.append(key)
                iteration_candidate_data[key] = value


            # winners = image_ranker.rank_images_mroz(
            #     [(k, x[0], x[1]) for k, v in iteration_library_data.items() for x in v],
            #     [(k, x[0], x[1]) for k, v in iteration_candidate_data.items() for x in v],
            #     matching_coefficient,
            #     absent_coefficient)

            # winners = image_ranker.rank_images_galajdator(
            #     [(k, x[0], x[1]) for k, v in iteration_library_data.items() for x in v],
            #     [(k, x[0], x[1]) for k, v in iteration_candidate_data.items() for x in v],
            #     5, model)
            # winners = image_ranker.rank_images_naive(
            #     [(k, x[0], x[1]) for k, v in iteration_library_data.items() for x in v],
            #     [(k, x[0], x[1]) for k, v in iteration_candidate_data.items() for x in v])
            winners = image_ranker.rank_images_random([(k, x[0], x[1]) for k, v in iteration_candidate_data.items() for x in v])


            total_score_sum = 0
            min_value = 0
            for filename, score, reasons in winners:
                if score < min_value:
                    min_value = score

            shifted_winners = []
            for filename, score, reasons in winners:
                shifted_winners += [(filename, score - min_value, reasons)]

            for filename, score, reasons in shifted_winners:
                total_score_sum += score

            normalized_validation_winners = []
            for filename, score, reasons in shifted_winners:
                if filename in mixed_candidates_from_library:
                    normalized_validation_winners += [(filename, score / total_score_sum, reasons)]


            score_sum = 0
            for filename, score, reasons in normalized_validation_winners:
                score_sum += score

            print("%f," % score_sum)


if __name__ == '__main__':
    test_ranking_algorithm = TestRankingAlgorithm()
    test_ranking_algorithm.run()
