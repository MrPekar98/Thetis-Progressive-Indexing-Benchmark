#!/bin/bash

set -e

RESULT_DIR="same_results/"
START_TIME=$(date +%s)
mkdir -p ${RESULT_DIR}

for QUERY in "similar_queries/"* ;\
do
    echo "Executing ${QUERY}"
    cp ${QUERY} ../TableSearch/queries/
    TIME_POINT="$(($(date +%s) - ${START_TIME}))s"
    sleep 30s

    QUERY_FILE=(${QUERY//// })
    QUERY_ID=(${QUERY_FILE[1]//./ })
    QUERY_ID=${QUERY_ID[0]}
    mkdir -p ${RESULT_DIR}${TIME_POINT}/
    cp -r ../TableSearch/data/search_output/${QUERY_ID}/ ${RESULT_DIR}${TIME_POINT}/
done
