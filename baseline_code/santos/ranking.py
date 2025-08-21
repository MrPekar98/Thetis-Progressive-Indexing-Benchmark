import sys
import os
import shutil
import json
import indexer
from mlfq import Mlfq
from statistics import mean

index_dir = '/index_dir'
indexed = 0.0
fraction = float(sys.argv[1])
limit = float(sys.argv[2])
task = sys.argv[3]
corpus = '/' + task
overlap = sys.argb[4]
query_dir = '/queries/' + overlap + '/'
result_dir = '/results/ranking/'
internal_indexes = '/indexes'
os.mkdir(internal_indexes)
os.mkdir(index_dir)

if not os.path.exists(result_dir):
    os.mkdir(result_dir)

while indexed < limit:
    indexed += fraction
    print('Colleting data to index at ' + str(indexed) + '%')
    indexer.index(indexed, corpus, index_dir)

    print('Pre-processing YAGO')
    os.system('python3 preprocess_yago.py')

    print('Type counting')
    os.system('python3 Yago_type_counter.py')

    print('Sub-class extraction')
    os.system('python3 Yago_subclass_extractor.py')

    print('Sub-class scoring')
    os.system('python3 Yago_subclass_score.py')

    print('Constructing inverted index')
    os.system('python3 data_lake_processing_yago.py ' + corpus + ' ' + task)

    print('Constructing synthesized type dictionary, relationship dictionary and synthesized inverted index')
    os.system('python3 data_lake_processing_synthesized_kb.py ' + corpus + ' ' + task)

    print('Querying SANTOS')
    os.system('python3 query_santos.py ' + task + ' ' + query_dir + ' ' + overlap)

    print()

print('Done')
