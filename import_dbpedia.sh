#!/bin/bash

set -e

NEO4J_HOME="/var/lib/neo4j/"
NEO4J_IMPORT="${NEO4J_HOME}import"
KG_DIR="/kg/"

echo "Cleaning the data"

for FILE in ${KG_DIR}*ttl ;\
do
    FILE_CLEAN="$(basename "${FILE}")"
    iconv -f utf-8 -t ascii -c "${FILE}" | grep -E '^<(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[A-Za-z0-9\+&@#/%?=~_|]>\W<' | grep -Fv 'xn--b1aew' > ${NEO4J_IMPORT}/${FILE_CLEAN}
done

echo "Importing the data"

for FILE in ${NEO4J_IMPORT} ;\
do
    FILENAME="$(basename "${FILE}")"
    ${NEO4J_HOME}/neo4j-server/bin/cypher-shell -u neo4j -p 'admin' "CALL n10s.rdf.import.fetch(\"file://${NEO4J_IMPORT}/${FILENAME}\",\"Turtle\");"
    rm ${FILE}
done
