import sys
import os
import numpy as np
from sklearn.metrics import ndcg_score
import math
import json

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

    with open(ground_truth_file, 'r') as handle:
        obj = json.load(handle)

        for table in obj['scores']:
            score = table['score']

            if math.isnan(score):
                score = 0.0

            ground_truth_scores[table['tableID']] = score

    return (list(result_scores.values()), list(ground_truth_scores.values()))

if len(sys.argv) < 3:
    print('Requires passing of overlap type and corpus name as parameters')
    exit(1)

overlap_type = sys.argv[1]
corpus = sys.argv[2]
gt_dir = '/results/chained_ground_truth/'

if overlap_type != 'low' and overlap_type != 'high':
    print('Overlap type must be either \'high\' or \'low\'')
    exit(1)

elif corpus == 'wikitables' or corpus == 'gittables':
    corpus = '/' + corpus + '/'

else:
    print('Did not recognize the corpus name \'' + corpus + '\'')
    exit(1)

result_dir = '/results/chained_ranking_' + overlap_type + '_overlap/'

if not os.path.exists(result_dir):
    print('Result directory \'' + result_dir + '\' does not exist')
    exit(1)

indexed_fractions = os.listdir(result_dir)
corpus_files = os.listdir(corpus)
progress = 0

with open('/results/chained_ndcg.txt', 'w') as handle:
    for fraction in indexed_fractions:
        query_results = os.listdir(result_dir + fraction + '/')
        handle.write(fraction + '%\n')

        print(' ' * 100, end = '\r')
        print('Progress: ' + str((progress / len(indexed_fractions)) * 100)[:5] + '%', end = '\r')
        progress += 1

        for result in query_results:
            result_file = result_dir + fraction + '/' + result + '/filenameToScore.json'
            gt_file = gt_dir + result + '/filenameToScore.json'
            scores = ranking_ndcg(result_file, gt_file, corpus_files)
            ndcg = ndcg_score(np.array([scores[1]]), np.array([scores[0]]), k = 10)
            handle.write(str(ndcg) + '\n')

        handle.write('\n')
