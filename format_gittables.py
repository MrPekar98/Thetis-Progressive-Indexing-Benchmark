import os
import zipfile
import json
import pandas as pd
import pyarrow

dir = 'gittables/'
zip_files = os.listdir(dir)
progress = 0

for zip_file in zip_files:
    print(' ' * 100, end = '\r')
    print('Progress (extracting): ' + str((progress / len(zip_files)) * 100)[:5] + '%', end = '\r')
    progress += 1

    with zipfile.ZipFile(dir + zip_file, 'r') as zip_ref:
        zip_ref.extractall(dir)

    os.remove(dir + zip_file)

progress = 0
parquet_files = os.listdir(dir)
id = 1
print()

for parquet_file in parquet_files:
    if not parquet_file.endswith('.parquet'):
        progress += 1
        continue

    print(' ' * 100, end = '\r')
    print('Progress (formatting): ' + str((progress / len(parquet_files)) * 100)[:5] + '%', end = '\r')
    progress += 1

    try:
        df = pd.read_parquet(dir + parquet_file)
        rows, cols = df.shape
        j = {'id': id, 'pgId': 1, 'numDataRows': rows, 'numCols': cols, 'pgTitle': parquet_file.split('.')[0], 'numNumericCols': 0, 'tableCaption': '', 'headers': [], 'rows': []}
        headers = list(df.columns.values)

        for header in headers:
            j['headers'].append({'text': header, 'isNumeric': False, 'links': []})

        for index, row in df.iterrows():
            j_row = []

            for header in headers:
                j_row.append({'text': row[header], 'isNumeric': isinstance(row[header], int) or isinstance(row[header], float), 'links': []})

            j['rows'].append(j_row)

        with open(dir + str(id) + '.json', 'w') as handle:
            json.dump(j, handle)

    except TypeError:
        pass

    except pyarrow.lib.ArrowInvalid:
        pass

    id += 1
    os.remove(dir + parquet_file)
