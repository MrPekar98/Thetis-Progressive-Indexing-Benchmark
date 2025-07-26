import json
import sys
import os
from neo4j import GraphDatabase

# Links a Wikipedia link to its corresponding DBpedia link
def entity_link(link):
    URI = 'neo4j://' + os.environ['NEO4J_HOST'] + ':7687'
    auth = ('neo4j', 'admin')

    with GraphDatabase.driver(URI, auth = auth) as driver:
        records = driver.execute_query("MATCH (a:Resource)-[p:ns109__isPrimaryTopicOf]->(b:Resource) WHERE b.uri IN [$link] RETURN a.uri AS uri", link = link.replace('http://www', 'http://en'))

        for record in records:
            if len(record) == 0:
                return None

            return record[0]['uri']

        return None

# Returns a 2-tuple containing first a list of rows and then a list of columns
# These coordinates represent a sub-table where all cells contain KG links
def coordinates(table):
    rows = [i for i in range(len(table))]
    columns = []
    largest_row = 0

    for row in table:
        column_i = 0
        largest_row = max(largest_row, len(row))

        for column in row:
            if len(column['links']) > 0 and not entity_link(column['links'][0]) is None:
                if not column_i in columns:
                    columns.append(column_i)

            column_i += 1

    row_i = 0

    for row in table:
        column_i = 0

        if len(row) != largest_row:
            rows.remove(row_i)

        else:
            for column in row:
                if column_i in columns and (len(column['links']) == 0 or (len(column['links']) > 0 and entity_link(column['links'][0]) is None)):
                    rows.remove(row_i)
                    break

                column_i += 1

        row_i += 1

    columns = sorted(columns)
    return [rows, columns]

if len(sys.argv) < 3:
    print('Missing input and output file')
    exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r') as in_handle:
    table = json.load(in_handle)
    query = {'queries': []}
    query_coordinates = coordinates(table['rows'])

    if len(query_coordinates[1]) == 0:
        exit(1)

    for row in query_coordinates[0]:
        query_row = []

        for column in query_coordinates[1]:
            link = table['rows'][row][column]['links'][0]
            entity = entity_link(link)
            query_row.append(entity)

        query['queries'].append(query_row)

    with open(output_file, 'w') as out_handle:
        json.dump(query, out_handle)
