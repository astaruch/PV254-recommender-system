import numpy as np
from scipy import spatial

def add_vector_rep(model, rows):
  new_rows = []
  for row in rows:
    filename, label, score = row
    new_rows += [(filename, label, score, model.word_rep(label))]

  return new_rows


def compute_cosine_similarity(vector1, vector2):
  result = 1 - spatial.distance.cosine(vector1, vector2)
  return result


def sigmoid(x):
  sigm = 1. / (1. + np.exp(-x))
  return sigm


def get_score_for_label(profile_labels_dict, label_vector_rep):
    score_for_label = 0
    for label, label_info in profile_labels_dict.items():
      vector_rep_label_from_library = label_info['vector_rep']
      count_of_label_occuring_in_profile = label_info['count']
      weight_factor_for_label = 10 * sigmoid(count_of_label_occuring_in_profile)
      score_for_label += (
            compute_cosine_similarity(label_vector_rep, vector_rep_label_from_library) * weight_factor_for_label)

    return score_for_label
