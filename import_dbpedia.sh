#!/bin/bash

set -e

NEO4J_HOME="/var/lib/neo4j/"
NEO4J_IMPORT="${NEO4J_HOME}import/"
KG_DIR="/kg/"

echo "Creating index"
${NEO4J_HOME}/bin/cypher-shell -u neo4j -p '12345678' "CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource) REQUIRE r.uri IS UNIQUE;"
${NEO4J_HOME}/bin/cypher-shell -u neo4j -p '12345678' 'call n10s.graphconfig.init( { handleMultival: "OVERWRITE",  handleVocabUris: "SHORTEN", keepLangTag: false, handleRDFTypes: "NODES" })'

echo "Cleaning the data"

for FILE in ${KG_DIR}*ttl ;\
do
    FILE_CLEAN="$(basename "${FILE}")"
    iconv -f utf-8 -t ascii -c "${FILE}" | grep -E '^<(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[A-Za-z0-9\+&@#/%?=~_|]>\W<' | grep -Fv 'xn--b1aew' > ${NEO4J_IMPORT}/${FILE_CLEAN}
done

echo "Importing the data"

for FILE in ${NEO4J_IMPORT}*ttl ;\
do
    FILENAME="$(basename "${FILE}")"
    ${NEO4J_HOME}bin/cypher-shell -u neo4j -p '12345678' "CALL n10s.rdf.import.fetch(\"file://${NEO4J_IMPORT}/${FILENAME}\",\"Turtle\");"
    rm ${FILE}
done
