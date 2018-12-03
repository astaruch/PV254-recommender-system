from collections import defaultdict, OrderedDict
from math import ceil


def rank_images_mroz(library_data, candidate_data, matching_coefficient, absent_coefficient):
    library_labels = defaultdict(lambda: {'total_score': 0.0, 'count': 0})
    for _, label, score in library_data:
        library_labels[label]['total_score'] += score
        library_labels[label]['count'] += 1

    candidate_labels = defaultdict(lambda: defaultdict(lambda: 0.0))
    for filename, label, score in candidate_data:
        candidate_labels[filename][label] = score

    for filename, labels in candidate_labels.items():
        candidate_labels[filename] = OrderedDict(sorted(labels.items(), key=lambda x: x[1], reverse=True))

    candidate_evaluation = defaultdict(lambda: {'absent_labels_count': 0,
                                                'matching_labels': defaultdict(lambda: {'own_score': 0.0,
                                                                                        'library_score': 0.0,
                                                                                        'library_count': 0})})

    for filename, labels in candidate_labels.items():
        for label, score in labels.items():
            if label in library_labels:
                candidate_evaluation[filename]['matching_labels'][label]['own_score'] = score
                candidate_evaluation[filename]['matching_labels'][label]['library_score'] = library_labels[label][
                    'total_score']
                candidate_evaluation[filename]['matching_labels'][label]['library_count'] = library_labels[label][
                    'count']
            else:
                candidate_evaluation[filename]['absent_labels_count'] += 1

    for filename, evaluation in candidate_evaluation.items():
        candidate_evaluation[filename]['score'] = 0.0
        candidate_evaluation[filename]['most_prominent'] = []
        for label, category_values in evaluation['matching_labels'].items():
            immediate_value = 0.0
            immediate_value += category_values['own_score'] / (
                        category_values['library_score'] / category_values['library_count'])
            immediate_value *= pow(matching_coefficient, category_values['library_count'])
            candidate_evaluation[filename]['score'] += immediate_value
            if len(candidate_evaluation[filename]['most_prominent']) < 3:
                candidate_evaluation[filename]['most_prominent'].append(label)
        candidate_evaluation[filename]['score'] -= absent_coefficient * evaluation['absent_labels_count']

    ordered_recommendations = OrderedDict(
        sorted(candidate_evaluation.items(), key=lambda x: x[1]['score'], reverse=True))

    winners = []

    for index, (filename, category_values) in enumerate(ordered_recommendations.items()):
        reasons = []
        reasons.append('Matches the target profile in {} labels.'.format(len(category_values['matching_labels'])))
        reasons.append('Labels matching the most are: {}.'.format(', '.join(category_values['most_prominent'])))
        reasons.append(
            'Differs from the target profile only in {} labels.'.format(category_values['absent_labels_count']))
        score = category_values['score']
        winners.append((filename, score, reasons))

    return winners
