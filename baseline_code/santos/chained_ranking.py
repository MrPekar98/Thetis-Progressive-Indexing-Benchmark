import sys
import os
import shutil
import json
import indexer
from statistics import mean
import time
from adapter import HistoricalAdapter

index_dir = '/index_dir'
mlfq_levels = 5
adapt_interval = 2.0
old_results = dict()
priority_boosts = dict()
indexed = 0.0
fraction = float(sys.argv[1])
limit = float(sys.argv[2])
task = sys.argv[3]
corpus = '/' + task
overlap = sys.argv[4]
query_dir = '/queries/' + overlap + '_overlap_csv/'
exp_query_dir = '/exp_queries/'
result_dir = '/results/chained_ranking/'
internal_indexes = '/indexes'
os.mkdir(internal_indexes)
os.mkdir(index_dir)
os.mkdir(exp_query_dir)

if not os.path.exists(result_dir):
    os.mkdir(result_dir)

initial_queries = os.listdir(query_dir)

for query in initial_queries:
    shutil.copy(query_dir + query, exp_query_dir + query)

while indexed < limit:
    indexed += fraction
    print('Colleting data to index at ' + str(indexed) + '%')
    indexer.index(indexed, corpus, index_dir, priority_boosts = priority_boosts)
    priority_boosts = dict()
    print('Indexing')

    start_time = time.time()
    os.system('python3 data_lake_processing_yago.py ' + index_dir + ' ' + task)
    os.system('python3 data_lake_processing_synthesized_kb.py ' + index_dir + ' ' + task)

    duration = time.time() - start_time
    print('Spent ' + str(duration) + 's indexing')

    if indexed - adapt_interval >= adapt_interval:
        adapt_interval = indexed
        adapt_dir = '/adapt_dir'
        os.mkdir(adapt_dir)
        print('Adapting to query workload')

        for query in old_results.keys():
            query_id = query.replace('.csv', '')
            result_corpus = list(old_results[query].keys())

            if 'wikipage' in query:
                shutil.copy(query_dir + query, adapt_dir + '/' + query)

            else:
                shutil.copy(corpus + '/' + query, adapt_dir + '/' + query)

            for table in result_corpus:
                table = table.split('.')[0] + '.csv'
                shutil.copy(corpus + '/' + table, adapt_dir + '/' + table)

            result_dataloader = CSVDataLoader(
                root_path = adapt_dir,
                sep = ','
            )
            new_qe = QueryEngine(name_index, format_index, value_index, embedding_index)
            query_table = result_dataloader.read_table(table_name = query_id)
            new_results, extended_new_results = new_qe.table_query(table = query_table, aggregator = lambda scores: mean(scores), k = 100, verbose = True)
            new_result = dict()

            for result in new_results:
                new_result[result[0]] = result[1]

            adapter = HistoricalAdapter(old_results[query], new_result, mlfq_levels)
            priority_boosts = adapter.adapt()

        shutil.rmtree(adapt_dir)

    print('Querying SANTOS')

    indexed_result_dir = result_dir + task + '_benchmark_result_by_santos/' + str(indexed)
    os.makedirs(indexed_result_dir)
    os.system('python3 query_santos.py ' + task + ' ' + exp_query_dir + ' ' + overlap + ' ' + indexed_result_dir)

    """for query in queries:
        query_id = query.replace('.csv', '')
        query_table = dataloader.read_table(table_name = query_id)
        results, extended_results = qe.table_query(table = query_table, aggregator = lambda scores: mean(scores), k = 100, verbose = True)
        old_results[query] = {}
        res_dict = {'scores': []}
        os.remove(exp_query_dir + query)
        os.remove(index_dir + '/' + query)

        result_table = results[0][0].split('.')[0] + '.csv'
        result_i = 0

        while not os.path.exists(corpus + '/' + result_table) and result_i < len(results):
            result_i += 1
            result_table = results[result_i][0].split('.')[0] + '.csv'

        shutil.copy(corpus + '/' + result_table, exp_query_dir + result_table)

        for result in results:
            res_dict['scores'].append({'tableID': result[0], 'score': result[1]})
            old_results[query][result[0]] = result[1]

        with open(result_dir + str(indexed) + '/' + query_id + '.json', 'w') as handle:
            json.dump(res_dict, handle)"""

    print()

print('Done')
