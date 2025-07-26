from probabilistic_mlfq import ProbabilisticMlfq
import os
import random
import csv
import math

indexed_rows = dict()
total_rows = -1

def index(percentage, corpus, index_dir):
    global indexed_rows
    global total_rows
    mlfq = ProbabilisticMlfq()

    if mlfq.size() == 0:
        print('Adding tables to MLFQ')
        mlfq.add_tables([corpus + '/' + table for table in os.listdir(corpus)])

    if total_rows == -1:
        total_rows = row_count(corpus)
        print('There\'s a total of ' + str(total_rows) + ' rows to index')

    rows_to_index = int(math.ceil((percentage / 100) * total_rows))
    progress = 0
    print('Indexing ' + str(rows_to_index) + ' rows')

    for i in range(rows_to_index):
        table_id = mlfq.poll()
        print(' ' * 100, end = '\r')
        print('Progress: ' + str((progress / rows_to_index) * 100)[:5] + '%', end = '\r')
        progress += 1

        if table_id is None:
            print('MLFQ is empty')
            break

        elif not table_id in indexed_rows.keys():
            indexed_rows[table_id] = list()

        already_indexed = indexed_rows[table_id]
        table = csv2table(table_id)
        table_rows = [row for row in range(len(table)) if not row in indexed_rows[table_id]]
        random_row = random.randint(0, len(table_rows) - 1)
        indexed_rows[table_id].append(random_row)

        if len(indexed_rows[table_id]) == len(table):
            mlfq.remove_table(table_id)

        else:
            if len(indexed_rows[table_id]) == 1:
                mlfq.move_table(table_id, mlfq.levels())

            else:
                current_level = mlfq.level_of(table_id)

                if current_level != -1 and current_level < mlfq.levels():
                    mlfq.move_table(table_id, current_level + 1)

    mlfq.checkpoint()

    synthetic_tables = os.listdir(index_dir)
    print('Cleaning directory from synthetic tables')

    for synthetic_table in synthetic_tables:
        os.remove(index_dir + '/' + synthetic_table)

    print('Constructing synthetic tables to index')
    construct_synthetic_tables(corpus, index_dir)

    print()

def row_count(directory):
    files = os.listdir(directory)
    count = 0

    for file in files:
        table = csv2table(directory + '/' + file)
        count += len(table)

    return count

def csv2table(path):
    table = list()

    with open(path, 'r') as handle:
        reader = csv.reader(handle)

        for row in reader:
            table.append(row)

    return table

def construct_synthetic_tables(corpus, index_dir):
    for table_id in indexed_rows.keys():
        table = csv2table(table_id)

        if len(indexed_rows[table_id]) > 0 and len(table[indexed_rows[table_id][0]]) > 0:
            with open(index_dir + '/' + table_id.split('/')[-1], 'w') as handle:
                writer = csv.writer(handle)

                for row_id in indexed_rows[table_id]:
                    writer.writerow(table[row_id])
