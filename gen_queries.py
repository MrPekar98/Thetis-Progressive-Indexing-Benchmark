import os
import json
import csv
import sys
import shutil

def to_csv(in_file, out_file):
    with open(in_file, 'r') as in_handle:
        json_table = json.load(in_handle)

        with open(out_file, 'w') as out_handle:
            csv_table = csv.writer(out_handle)

            for row in json_table['queries']:
                csv_row = list()

                for cell in row:
                    csv_row.append(cell.split('/')[-1].replace('_', ' '))

                csv_table.writerow(csv_row)

if len(sys.argv) < 2:
    print('Missing argument: number of queries')
    exit(1)

num_queries = int(sys.argv[1])
queries_dir = 'queries/'
row_1_dir = queries_dir + '1-row/'
row_5_dir = queries_dir + '5-row/'
json_row_1_dir = queries_dir + 'json_1-row/'
json_row_5_dir = queries_dir + 'json_5_row/'
tuple_dir = 'SemanticTableSearchDataset/queries/2019/'
tuple_1_dir = tuple_dir + '1_tuples_per_query/'
tuple_5_dir = tuple_dir + '5_tuples_per_query/'

if not os.path.exists(queries_dir):
    os.mkdir(queries_dir)
    os.mkdir(row_1_dir)
    os.mkdir(row_5_dir)
    os.mkdir(json_row_1_dir)
    os.mkdir(json_row_5_dir)

counter = 0
tuple_1_files = os.listdir(tuple_1_dir)
tuple_5_files = os.listdir(tuple_5_dir)
print('Generating ' + str(num_queries) + ' queries of 1 row...')

for file in tuple_1_files:
    if counter >= num_queries:
        break

    to_csv(tuple_1_dir + file, row_1_dir + file.replace('.json', '.csv'))
    shutil.copyfile(tuple_1_dir + file, json_row_1_dir + file)
    counter += 1

counter = 0
print('Generating ' + str(num_queries) + ' queries of 5 rows...')

for file in tuple_5_files:
    if counter >= num_queries:
        break

    to_csv(tuple_5_dir + file, row_5_dir + file.replace('.json', '.csv'))
    shutil.copyfile(tuple_5_dir + file, json_row_5_dir + file)
    counter += 1

print('Done')
