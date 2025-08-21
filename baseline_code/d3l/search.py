import sys
import os
import shutil
import json
from statistics import mean

import numpy as np
from d3l.indexing.similarity_indexes import NameIndex, FormatIndex, ValueIndex, EmbeddingIndex, DistributionIndex
from d3l.input_output.dataloaders import CSVDataLoader
from d3l.querying.query_engine import QueryEngine
from d3l.utils.functions import pickle_python_object, unpickle_python_object

corpus = '/' + os.getenv('CORPUS') + '/'
query_dir = '/queries/' + os.getenv('OVERLAP') + '_overlap_csv/'
result_dir = '/results/gt/'
index_dir = '/index/'
table_files = os.listdir(corpus)
os.mkdir(index_dir)

if not os.path.exists(result_dir):
    os.mkdir(result_dir)

for table in table_files:
    shutil.copy(corpus + table, index_dir + table)

dataloader = CSVDataLoader(
    root_path = index_dir,
    sep = ','
)

name_index = NameIndex(dataloader = dataloader)
pickle_python_object(name_index, './name.lsh')
print("Name index: finished!")

format_index = FormatIndex(dataloader = dataloader)
pickle_python_object(format_index, './format.lsh')
print("Format: finished!")

value_index = ValueIndex(dataloader = dataloader)
pickle_python_object(value_index, './value.lsh')
print("Value: finished!")

embedding_index = EmbeddingIndex(dataloader = dataloader, index_cache_dir = './')
pickle_python_object(embedding_index, './embedding.lsh')
print("Embedding: finished!")

print('Querying D3L')

qe = QueryEngine(name_index, format_index, value_index, embedding_index)
queries = os.listdir(query_dir)

for query in queries:
    shutil.copy(query_dir + query, index_dir + query)

    query_id = query.replace('.csv', '')
    query_table = dataloader.read_table(table_name = query_id)
    results, extended_results = qe.table_query(table = query_table, aggregator = lambda scores: mean(scores), k = 100, verbose = True)
    res_dict = {'scores': []}

    for result in results:
        res_dict['scores'].append({'tableID': result[0], 'score': result[1]})

    with open(result_dir + '/' + query_id + '.json', 'w') as handle:
        json.dump(res_dict, handle)

print('Done')
