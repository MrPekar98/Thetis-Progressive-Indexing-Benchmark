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
# The implementation is simplified for now: just the largest row
def coordinates(matrix):
    largest_row_i = -1
    i = 0
    columns = []

    for row in matrix:
        tmp_columns = []
        j = 0

        for column in row:
            if len(column['links']) > 0 and not entity_link(column['links'][0]) is None:
                tmp_columns.append(j)

            j += 1

        if len(tmp_columns) > len(columns):
            largest_row_i = i
            columns = tmp_columns

        i += 1

    return [[largest_row_i], columns]

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
