import json
import sys

if len(sys.argv) < 3:
    print('Missing input path and/or result index')
    exit(1)

file = sys.argv[1]
index = int(sys.argv[2])

if index < 0:
    print('Index cannot be negative')
    exit(1)

with open(file, 'r') as handle:
    results = json.load(handle)
    i = 0

    if index >= len(results['scores']):
        print('Index greater than the number of results')
        exit(1)

    for result in results['scores']:
        table_id = result['tableID']

        if i == index:
            print(table_id)
            break

        i += 1
