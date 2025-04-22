import sys
import os
import shutil

if len(sys.argv) < 3:
    print('Overlap type and corpus name are required as parameters')
    exit(1)

overlap_type = sys.argv[1]
corpus = sys.argv[2]
results_dir = '/results/chained_ranking_' + overlap_type + '_overlap/'
query_dir = '/TableSearch/queries/'

if not os.path.exists(results_dir):
    print('Directory with overlap type \'' + overlap_type + '\' does not exist')
    exit(1)

elif corpus != 'wikitables' and corpus != 'gittables':
    print('Corpus name \'' + corpus + '\' was not recognized')
    exit(1)

file_ids = set()
indexing_points = os.listdir(results_dir)
corpus = '/' + corpus + '/'

for indexing_point in indexing_points:
    ids = os.listdir(results_dir + indexing_point)

    for id in ids:
        file_ids.add(id)

for file_id in file_ids:
    if 'wikipage' in file_id and os.path.exists('/queries/' + overlap_type + '_overlap/' + file_id + '.json'):
        shutil.copy('/queries/' + overlap_type + '_overlap/' + file_id + '.json', query_dir + file_id + '.json')

    elif os.path.exists(corpus + file_id + '.json'):
        os.system('python3 to_query.py ' + corpus + file_id + '.json ' + query_dir + file_id + '.json')
