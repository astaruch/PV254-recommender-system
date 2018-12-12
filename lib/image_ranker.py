from collections import defaultdict, OrderedDict
from operator import itemgetter
from math import ceil
from random import shuffle
from lib.lexvec_model import lexvec_model
from lib import galajdator_utils

def rank_images_naive(library_data, candidate_data):
    tags_dict = {}
    for _, label, _ in library_data:
        if label not in tags_dict:
            tags_dict[label] = 1
        else:
            tags_dict[label] += 1

    candidates = {}
    for filename, label, _ in candidate_data:
        if label in tags_dict:
            if filename in candidates:
                candidates[filename] += tags_dict[label]
            else:
                candidates[filename] = tags_dict[label]
    candidates_sorted = OrderedDict(sorted(candidates.items(),
                                           key=itemgetter(1),
                                           reverse=True))
    winners = []
    for filename, score in candidates_sorted.items():
        winners.append((filename, score, []))
    return winners


def rank_images_random(candidate_data):
    random_values = [i for i in range(len(candidate_data))]
    shuffle(random_values)
    winners = []
    for index, el_idx in enumerate(random_values):
        winner = candidate_data[el_idx]
        winners.append((winner[0], len(candidate_data) - index, []))
    return winners


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

def rank_images_galajdator(library_data, candidate_data, pick_top_k_reasons = 5):
    model = lexvec_model.Model('./lib/lexvec_model/lexvec_model.bin')

    train_library_data_with_vector_rep = galajdator_utils.add_vector_rep(model, library_data)
    candidate_data_with_vector_rep = galajdator_utils.add_vector_rep(model, candidate_data)

    scores_candidate_data = defaultdict(lambda: {
        'sum': 0.0,
        'label_contributions': defaultdict(lambda: 0.0),
    })

    profile_labels = defaultdict(lambda: {
        'count': 0
    })

    for row in train_library_data_with_vector_rep:
        filename, label, score, vector_rep = row
        profile_labels[label]['count'] += 1
        profile_labels[label]['vector_rep'] = vector_rep


    for row in candidate_data_with_vector_rep:
        filename, label, score, label_vector_rep = row

        label_contribution = galajdator_utils.get_score_for_label(profile_labels, label_vector_rep)
        scores_candidate_data[filename]['sum'] += label_contribution
        scores_candidate_data[filename]['label_contributions'][label] = label_contribution


    results = []
    for filename, candidate_score in scores_candidate_data.items():
        reasons = []
        label_contributions_sorted = OrderedDict(
            sorted(candidate_score['label_contributions'].items(), key=lambda x: x[1], reverse=True))

        for label, label_contribution in label_contributions_sorted.items():
            reasons += ['Detected label "%s" had similarity score with profile: %f.' % (label, label_contribution)]
        results += [(filename, candidate_score['sum'], reasons[:pick_top_k_reasons])]

    # sort by score (second element in tuple)
    results = sorted(results, key=lambda tuple: -tuple[1])

    return results
