import os
import json
import csv
import sys

in_dir = sys.argv[1]
out_dir = in_dir

if not os.path.exists(in_dir):
    print('Path \'' + in_dir + '\' does not exist')
    exit(1)

if out_dir.endswith('/'):
    out_dir = out_dir[:-1]

out_dir += '_csv/'
files = os.listdir(in_dir)
progress = 0

os.mkdir(out_dir)

for file in files:
    print(' ' * 100, end = '\r')
    print('Progress: ' + str((progress / len(files)) * 100)[:5] + '%', end = '\r')
    progress += 1

    with open(in_dir + file, 'r') as in_handle:
        try:
            table = json.load(in_handle)

            with open(out_dir + file, 'w') as out_handle:
                writer = csv.writer(out_handle)
                headers = []

                for header in table['headers']:
                    headers.append(header['text'])

                writer.writerow(headers)

                for row in table['rows']:
                    tuple = []

                    for cell in row:
                        tuple.append(cell['text'])

                    writer.writerow(tuple)

        except json.decoder.JSONDecodeError as e:
            pass
