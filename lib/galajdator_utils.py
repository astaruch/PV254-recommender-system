import numpy as np
from scipy import spatial

def add_vector_rep(model, rows):
  new_rows = []
  vector_rep_mapping = {}
  for row in rows:
    filename, label, score = row
    if label not in vector_rep_mapping:
      vector_rep = model.word_rep(label)
      new_rows += [(filename, label, score, vector_rep)]
      vector_rep_mapping[label] = vector_rep
    else:
      new_rows += [(filename, label, score, vector_rep_mapping[label])]


  return new_rows


def compute_cosine_similarity(vector1, vector2):
  result = 1 - spatial.distance.cosine(vector1, vector2)
  return result


def sigmoid(x):
  sigm = 1. / (1. + np.exp(-x))
  return sigm


def get_score_for_label(profile_labels_dict, label_vector_rep, scale_sigmoid_param = 10):
    score_for_label = 0
    for label, label_info in profile_labels_dict.items():
      vector_rep_label_from_library = label_info['vector_rep']
      count_of_label_occuring_in_profile = label_info['count']
      weight_factor_for_label = scale_sigmoid_param * sigmoid(count_of_label_occuring_in_profile)
      score_for_label += (
            compute_cosine_similarity(label_vector_rep, vector_rep_label_from_library) * weight_factor_for_label)

    return score_for_label
