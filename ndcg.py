import sys
import os
import json
import numpy as np
from sklearn.metrics import ndcg_score
import math

def ranking_ndcg(result_file, ground_truth_file, corpus):
    ground_truth_scores = {table:0 for table in corpus}
    result_scores = {table:0 for table in corpus}

    with open(result_file, 'r') as handle:
        obj = json.load(handle)

        for table in obj['scores']:
            score = table['score']

            if math.isnan(score):
                score = 0.0

            result_scores[table['tableID']] = score

    with open(groun_truth_file, 'r') as handle:
        obj = json.load(handle)

        for table in obj['scores']:
            score = table['score']

            if math.isnan(score):
                score = 0.0

            ground_truth_scores[table['tableID']] = score

    return (list(result_scores.values()), list(ground_truth_scores.values()))

corpus_dir = 'SemanticTableSearchDataset/table_corpus/tables_2019/'
corpus = os.listdir(corpus_dir)
gt_dir = 'results/ground_truth/'
results = 'results/ranking/'
time_points = os.listdir(results)
query_ids = os.listdir(gt_dir)

with open('ndcg.txt', 'w') as handle:
    for time_point in time_points:
        handle.write(time_point + 's\n')

        for query_id in query_ids:
            result_file = results + time_point + '/' query_id + '/filenameToScore.json'
            ground_truth_file = gt_dir + query_id + '/filenameToScore.json'
            ndcg = ranking_ndcg(result_file, ground_truth_file, corpus)
            handle.write(str(ndcg) + '\n')

        handle.write('\n')