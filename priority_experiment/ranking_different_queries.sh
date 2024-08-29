#!/bin/bash

set -e

RESULT_DIR="different_results/"
LOG_FILE="../TableSearch/data/log.txt"
THETIS_RESULT_DIR="../TableSearch/data/search_output/"
START_TIME=$(date +%s)
QUERY_LIMIT=10
TABLES=$(ls corpus/ | wc -l)
mkdir -p ${RESULT_DIR}
sleep 5m

while [[ $(tail -n 3 ${LOG_FILE} | head -n 1) != *"Fully indexed $((${TABLES} - 1))"* ]]
do
    QUERY_COUNT=0
    TIME_POINT="$(($(date +%s) - ${START_TIME}))s"
    mkdir -p ${RESULT_DIR}${TIME_POINT}/

    echo
    echo "Executing queries at time point ${TIME_POINT}"

    for QUERY in "different_queries/"* ;\
    do
        QUERY_COUNT=$((${QUERY_COUNT} + 1))
        echo "Adding ${QUERY} to the query queue"
        cp ${QUERY} ../TableSearch/queries/

        if [[ ${QUERY_COUNT} == ${QUERY_LIMIT} ]]
        then
            break
        fi
    done

    sleep 5m

    for RESULT in "${THETIS_RESULT_DIR}"* ;\
    do
        cp -r ${RESULT} ${RESULT_DIR}${TIME_POINT}/
    done

    rm -r 
done

# Get the final ranking when progressiv indexing is done
echo
echo "Final query executions"

QUERY_COUNT=0
mkdir -p "${RESULT_DIR}final/"

for QUERY in "different_queries/"* ;\
do
    echo "Adding ${QUERY} to the query queue"
    cp ${QUERY} ../TableSearch/queries/
    QUERY_COUNT=$((${QUERY_COUNT} + 1))

    if [[ ${QUERY_COUNT} == ${QUERY_LIMIT} ]]
    then
        break
    fi
done

sleep 5m

for RESULT in "${THETIS_RESULT_DIR}"* ;\
do
    cp -r ${RESULT} "${RESULT_DIR}final/"
done

echo
echo "Done"
