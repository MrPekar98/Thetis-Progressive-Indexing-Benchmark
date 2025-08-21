import sys
import os
import json
import numpy as np
from sklearn.metrics import ndcg_score
import math

def ranking_ndcg(result_file, ground_truth_file, corpus):
    ground_truth_scores = {table.split('.')[0]:0 for table in corpus}
    result_scores = {table.split('.')[0]:0 for table in corpus}

    with open(result_file, 'r') as handle:
        obj = json.load(handle)

        for table in obj['scores']:
            score = table['score']

            if math.isnan(score):
                score = 0.0

            result_scores[table['tableID'].split('.')[0]] = score

    with open(ground_truth_file, 'r') as handle:
        obj = json.load(handle)

        for table in obj['scores']:
            score = table['score']

            if math.isnan(score):
                score = 0.0

            ground_truth_scores[table['tableID'].split('.')[0]] = score

    return (list(result_scores.values()), list(ground_truth_scores.values()))

corpus_dir = 'SemanticTableSearchDataset/table_corpus/tables_2019/'

if sys.argv[1] == 'gittables':
    corpus_dir = 'gittables/'

if len(sys.argv) > 2:
    corpus_dir = corpus_dir[:len(corpus_dir) - 12] + 'csv_tables_2019/'

corpus = os.listdir(corpus_dir)
gt_dir = 'results/ground_truth/'
results = 'results/ranking/'
ndcg_file = '/results/ndcg.txt'

if len(sys.argv) > 2:
    if sys.argv[2] == 'd3l':
        results = 'results/d3l/ranking/'
        gt_dir = 'results/d3l/gt/'
        ndcg_file = 'results/' + sys.argv[2] + '/ndcg.txt'

fractions = os.listdir(results)
query_ids = os.listdir(gt_dir)
k = 100

with open(ndcg_file, 'w') as handle:
    for fraction in fractions:
        handle.write(fraction + '%\n')

        for query_id in query_ids:
            result_file = results + fraction + '/' + query_id + '/filenameToScore.json'

            if len(sys.argv) > 2:
                result_file = results + fraction + '/' + query_id

            ground_truth_file = gt_dir + query_id + '/filenameToScore.json'

            if len(sys.argv) > 2:
                ground_truth_file = gt_dir + query_id

            scores = ranking_ndcg(result_file, ground_truth_file, corpus)
            ndcg = ndcg_score(np.array([scores[1]]), np.array([scores[0]]), k = k)
            handle.write(str(ndcg) + '\n')

        handle.write('\n')
