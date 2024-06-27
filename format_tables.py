import os
import json

progress = 0
in_dir = 'SemanticTableSearchDataset/table_corpus/tables_2019/'
out_dir = 'SemanticTableSearchDataset/table_corpus/jazero_corpus/'
in_files = os.listdir(in_dir)

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

for file in in_files:
    print(' ' * 100, end = '\r')
    print('Progress: ' + str((progress / len(in_files)) * 100)[:5] + '%', end = '\r')
    progress += 1

    with open(in_dir + file, 'r') as in_handle:
        with open(out_dir + file, 'w') as out_handle:
            table = json.load(in_handle)
            formated = {
                '_id': table['_id'],
                'numCols': table['numCols'],
                'numDataRows': table['numDataRows'],
                'numNumericCols': table['numNumericCols'],
                'headers': [],
                'rows': []
            }

            for header in table['headers']:
                formated['headers'].append({'text': header['text'], 'isNumeric': header['isNumeric']})

            for row in table['rows']:
                formated_row = []

                for cell in row:
                    text = ''

                    if len(cell['links']) > 0:
                        text = cell['links'][0].replace('"http://www.wikipedia.org/wiki/', '')

                    else:
                        text = cell['text']

                    formated_row.append({'text': text})

                formated['rows'].append(formated_row)

            json.dump(formated, out_handle)
