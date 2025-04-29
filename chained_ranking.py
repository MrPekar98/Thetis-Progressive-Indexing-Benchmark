import json
import os
import sys
import shutil
from pathlib import Path
import time

period = 2.0
type = os.environ['TYPE']
corpus = os.environ['CORPUS']
result_dir = '/results/chained_ranking_' + type + '_overlap/'
initial_queries = 'initial_queries/'
exp_queries = 'experiment_queries/'
thetis_dir = '/TableSearch/'
query_dir = thetis_dir + 'queries/'
log_file = thetis_dir + 'data/log.txt'
output_dir = thetis_dir + 'data/output/search_output/'

def progress():
    check_str = 'INFO: Indexed'
    line = ''

    while not check_str in line:
        with open(log_file, 'rb') as file:
            file.seek(-2, 2)

            while file.read(1) != b'\n':
                file.seek(-2, 1)

            line = file.readline().decode()

    return float(line.split(' ')[-1].replace('%', ''))

def select_result_table(file, index):
    if index < 0:
        return None

    with open(file, 'r') as handle:
        results = json.load(handle)
        i = 0

        if index >= len(results['scores']):
            return None

        for result in results['scores']:
            table_id = result['tableID']

            if i == index:
                return table_id

            i += 1

    return None

if type != 'low' and type != 'high':
    print('Type must be either \'low\' or \'high\'')
    exit(1)

elif corpus != 'wikitables' and corpus != 'gittables':
    print('Corpus must be either \'wikitables\' or \'gittables\'')
    exit(1)

initial_queries = initial_queries + type + '_overlap/'

if os.path.exists(result_dir):
    shutil.rmtree(result_dir)

os.mkdir(result_dir)
os.mkdir(exp_queries)

for item in Path(initial_queries).iterdir():
    dest = Path(exp_queries) / item.name
    shutil.copy2(item, dest)

time.sleep(2)

start = progress()
current = start
prev = current
limit = 30.0
iteration = 0
num_queries = len(os.listdir(initial_queries))
corpus_dir = '/wikitables/'

if corpus == 'gittables':
    corpus_dir = '/gittables/'

while current < limit:
    iteration += 1

    # Wait until next period
    while current - prev < period:
        time.sleep(1)

        current = progress()

    if len(os.listdir(query_dir)) > 0:
        for item in Path(query_dir).iterdir():
            os.remove(item)

    prev = current
    current = int(str(current).split('.')[0])
    print('Executing queries in iteration ' + str(iteration) + ' after having indexed ' + str(current) + '% of the data')

    for item in Path(exp_queries).iterdir():
        shutil.move(exp_queries + item.name, query_dir + item.name)

    # Wait until all queries have been executed
    while len(os.listdir(query_dir)) > 0:
        time.sleep(3)

    os.mkdir(result_dir + str(current))
    print('Saving results and constructing new queries')

    for item in Path(output_dir).iterdir():
        shutil.move(output_dir + item.name, result_dir + str(current) + '/' + item.name)

    # Constrct new queries
    for result in os.listdir(result_dir + str(current)):
        output_file = 'non'
        index = 0
        result_file = result_dir + str(current) + '/' + result + '/filenameToScore.json'

        while not os.path.exists(output_file):
            if index == num_queries:
                break

            table_id = select_result_table(result_file, index)

            if table_id is None:
                index += 1
                continue

            table_file = corpus_dir + table_id
            output_file = exp_queries + table_id
            index += 1
            os.system('python3 to_query.py ' + table_file + ' ' + output_file)

print('\nDone. Reached indexing limit ' + str(limit) + '.')
