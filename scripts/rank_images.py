import argparse
import os
import sqlite3
from collections import defaultdict, OrderedDict


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

        matching_coefficient = 1.03
        absent_coefficient = 0.87

        for filename, evaluation in candidate_evaluation.items():
            candidate_evaluation[filename]['score'] = 0.0
            candidate_evaluation[filename]['most_prominent'] = []
            for label, values in evaluation['matching_labels'].items():
                immediate_value = 0.0
                immediate_value += values['own_score'] / (values['library_score'] / values['library_count'])
                immediate_value *= pow(matching_coefficient, values['library_count'])
                candidate_evaluation[filename]['score'] += immediate_value
                if len(candidate_evaluation[filename]['most_prominent']) < 3:
                    candidate_evaluation[filename]['most_prominent'].append(label)
            candidate_evaluation[filename]['score'] -= absent_coefficient * evaluation['absent_labels_count']


        # Prepare best candidates as tuples (filename, score, list of reasons).
        # TODO: 1) order candidate_evaluation by 'score' in descending order
        #       2) select first n (n = self.options.count) best recommendations
        #       3) build winners list (use 'Matches in X labels.', 'Doesn't match only in Y labels.', 'Matches very strongly in labels 'most_prominent'')
        # ordered_recommendations = OrderedDict(sorted())
        # winners = []
        #
        # for index, item in enumerate(ordered_recommendations):
        #     if index >= self.options.count:
        #         break
        #     winners.append(item.key, item.v)


        output_filename_string = os.path.join(
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
