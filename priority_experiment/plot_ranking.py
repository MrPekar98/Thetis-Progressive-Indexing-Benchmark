import sys
import os
import json
import numpy as np
from sklearn.metrics import ndcg_score

results_dir = sys.argv[1]
corpus_dir = 'corpus/'
corpus = os.listdir(corpus_dir)
plot_dir = 'plots_data/'

if not os.path.exists(results_dir):
    print('Results directory \'' + results_dir + '\' does not exist')
    exit(1)

if not os.path.exists(plot_dir):
    os.mkdir(plot_dir)

def ranking_ndcg(test_file, expected_file, corpus):
    expected_scores = {table:0 for table in corpus}
    test_scores = {table:0 for table in corpus}

    with open(test_file, 'r') as handle:
        obj = json.load(handle)

        for table in obj['scores']:
            test_scores[table['tableID']] = table['score']

    with open(expected_file, 'r') as handle:
        obj = json.load(handle)

        for table in obj['scores']:
            expected_scores[table['tableID']] = table['score']

    return (list(test_scores.values()), list(expected_scores.values()))

time_points = os.listdir(results_dir)
gt_results = results_dir + '/final/'
query_ids = os.listdir(gt_results)
time_points.remove('final')

with open(plot_dir + 'ndcg.txt', 'w') as handle:
    for time_point in time_points:
        handle.write(time_point + '\n')

        for query_id in query_ids:
            test_file = results_dir + '/' + time_point + '/' + query_id + '/filenameToScore.json'
            expected_file = gt_results + query_id + '/filenameToScore.json'
            scores = ranking_ndcg(test_file, expected_file, corpus)
            ndcg = ndcg_score(np.array([scores[1]]), np.array([scores[0]]), k = 10)
            handle.write(str(ndcg) + '\n')

        handle.write('\n')
