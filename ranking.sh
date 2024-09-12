#!/bin/bash

set -e

PERIOD=$1
NUM_QUERIES=$2
OUTPUT_DIR="results/ranking/"
QUERY_DIR="SemanticTableSearchDataset/queries/2019/1_tuples_per_query/"
THETIS_QUERY_DIR="TableSearch/queries/"

mkdir -p ${OUTPUT_DIR}

if [[ ${PERIOD} < 1 || ${NUM_QUERIES} < 1 ]]
then
    echo "Number of queries and period must be at least 1"
    exit 1
fi

START=$(date +%s)
CURRENT=${START}
LIMIT=$(((60 * 60) / 2))

while [[ $((${CURRENT} - ${START})) < ${LIMIT} ]]
do
    COUNT=0
    echo "Adding ${NUM_QUERIES} to the query queue at time point $((${CURRENT} - ${START}))m"

    for QUERY in "${QUERY_DIR}"* ;\
    do
        COUNT=$((${COUNT} + 1))
        cp ${QUERY} ${THETIS_QUERY_DIR}

        if [[ ${COUNT} == ${NUM_QUERIES} ]]
        then
            break
        fi
    done

    sleep ${PERIOD}s
    CURRENT=$(date +%s)
done

echo
echo "Done executing queries"
echo "You can stop progressive indexing in Thetis now"
