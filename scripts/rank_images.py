import argparse
import os
import sqlite3
from collections import defaultdict, OrderedDict
from math import ceil

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
        parser.add_argument('--count', type=int, default=7, required=False,
                            help='Count of recommendations.')
        parser.add_argument('--dbfile', type=str, default='db.sqlite3', required=False,
                            help='Database sqlite3 file where output should be stored.')
        parser.add_argument('--positive', type=float, default=1.033, required=False,
                            help='Coefficient to fine-tune the scoring for matching labels.')
        parser.add_argument('--negative', type=float, default=1.44, required=False,
                            help='Coefficient to fine-tune the scoring for non-matching labels.')
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

        library_labels = defaultdict(lambda: {'total_score': 0.0, 'count': 0})
        for _, label, score in library_data:
            library_labels[label]['total_score'] += score
            library_labels[label]['count'] += 1

        candidate_labels = defaultdict(lambda: defaultdict(lambda: 0.0))
        for filename, label, score in candidate_data:
            candidate_labels[filename][label] = score

        for filename, labels in candidate_labels.items():
            candidate_labels[filename] = OrderedDict(sorted(labels.items(), key=lambda x: x[1], reverse=True))

        candidate_evaluation = defaultdict(lambda: {'absent_labels_count': 0, \
                                                    'matching_labels': defaultdict(lambda: {'own_score': 0.0, \
                                                                                            'library_score': 0.0, \
                                                                                            'library_count': 0})})

        for filename, labels in candidate_labels.items():
            for label, score in labels.items():
                if label in library_labels:
                    candidate_evaluation[filename]['matching_labels'][label]['own_score'] = score
                    candidate_evaluation[filename]['matching_labels'][label]['library_score'] = library_labels[label]['total_score']
                    candidate_evaluation[filename]['matching_labels'][label]['library_count'] = library_labels[label]['count']
                else:
                    candidate_evaluation[filename]['absent_labels_count'] += 1

        matching_coefficient = self.options.positive
        absent_coefficient = self.options.negative

        for filename, evaluation in candidate_evaluation.items():
            candidate_evaluation[filename]['score'] = 0.0
            candidate_evaluation[filename]['most_prominent'] = []
            for label, category_values in evaluation['matching_labels'].items():
                immediate_value = 0.0
                immediate_value += category_values['own_score'] / (category_values['library_score'] / category_values['library_count'])
                immediate_value *= pow(matching_coefficient, category_values['library_count'])
                candidate_evaluation[filename]['score'] += immediate_value
                if len(candidate_evaluation[filename]['most_prominent']) < 3:
                    candidate_evaluation[filename]['most_prominent'].append(label)
            candidate_evaluation[filename]['score'] -= absent_coefficient * evaluation['absent_labels_count']

        ordered_recommendations = OrderedDict(sorted(candidate_evaluation.items(), key=lambda x: x[1]['score'], reverse=True))

        winners = []
        max_score = -float('inf')
        for index, (filename, category_values) in enumerate(ordered_recommendations.items()):
            if index < self.options.count:
                if category_values['score'] > max_score:
                    max_score = category_values['score']
                reasons = []
                reasons.append('Matches the target profile in {} labels.'.format(len(category_values['matching_labels'])))
                reasons.append('Labels matching the most are: {}.'.format(', '.join(category_values['most_prominent'])))
                reasons.append('Differs from the target profile only in {} labels.'.format(category_values['absent_labels_count']))
                score = ceil(category_values['score'] / max_score * 100)
                winners.append((filename, '{}%'.format(score), reasons))


        output_filename_string = os.path.join(
            self.options.input,
            self.options.output)

        print('Generating output file: %s.' % output_filename_string)
        with open(output_filename_string, 'w') as output_file:
            output_file.write('<head>\n<body>\n</head>\n')

            count = 0
            for (filename, score, reasons) in winners:
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
