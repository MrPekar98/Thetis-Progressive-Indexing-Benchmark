import json
import os
import sys
from neo4j import GraphDatabase

table_dir = '/home/SemanticTableSearchDataset/table_corpus/tables_2019/'
out_file = '/home/entity-links.json'
tables = os.listdir(table_dir)
links = dict()
progress = 0
size = len(tables)
URI = 'neo4j://' + sys.argv[1]
AUTH = ('neo4j', '12345678')

with GraphDatabase.driver(URI, auth = AUTH) as driver:
    driver.verify_connectivity()

    for table in tables:
        print(' ' * 100, end = '\r')
        print('Progress: ' + str((progress / size) * 100)[:5] + '%', end = '\r')
        progress += 1

        with open(table_dir + table, 'r') as handle:
            tab = json.load(handle)

            for row in tab['rows']:
                for column in row:
                    if len(column['links']) > 0:
                        wikipedia = column['links'][0].replace('http://www', 'http://en')
                        query = 'MATCH (a:Resource)-[p:ns109__isPrimaryTopicOf]->(b:Resource) WHERE b.uri IN [$wikipedia] RETURN a.uri AS entity'
                        records, summary, keys = driver.execute_query(query, wikipedia = wikipedia, database_ = 'neo4j')

                        for record in records:
                            entity = record['entity']
                            links[wikipedia.split('/')[-1]] = entity.split('/')[-1]

with open(out_file, 'w') as handle:
    json.dump(links, handle)
