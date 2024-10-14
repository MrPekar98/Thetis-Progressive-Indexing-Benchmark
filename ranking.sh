#!/bin/bash

set -e

PERIOD=$1
NUM_QUERIES=$2
OUTPUT_DIR="results/ranking/"
QUERY_DIR="SemanticTableSearchDataset/queries/2019/1_tuples_per_query/"
THETIS_QUERY_DIR="TableSearch/queries/"
THETIS_OUTPUT_DIR="TableSearch/data/output/search_output/"

fraction()
{
    FILE="$1"
    CHECK_STR="INFO: Indexed"
    LINE=""
    INDEXED=""

    while [[ ${LINE} != *"${CHECK_STR}"* ]]
    do
        LINE=$(grep "${CHECK_STR}" ${FILE} | tail -n 1)
        INDEXED=(${LINE// / })
        INDEXED=${INDEXED[9]:0:4}
    done

    echo ${INDEXED}
}

mkdir -p ${OUTPUT_DIR}
sleep 2s

if [[ ${PERIOD} < 0 ]]
then
    echo "Period (data index fraction) must be greater than 0"
    exit 1
elif [[ ${NUM_QUERIES} < 1 ]]
then
    echo "Number of queries must be at least 1"
    exit 1
fi

LOG_FILE="TableSearch/data/log.txt"
START=$(fraction ${LOG_FILE})
CURRENT=${START}
PREV=${CURRENT}
LIMIT="30.00"
ITERATION=0

while [ $(echo "${CURRENT} < ${LIMIT}" | bc -l) ]
do
    COUNT=0
    echo "Adding ${NUM_QUERIES} to the query queue at fraction point ${CURRENT}"

    for QUERY in "${QUERY_DIR}"* ;\
    do
        COUNT=$((${COUNT} + 1))
        cp ${QUERY} ${THETIS_QUERY_DIR}

        if [[ ${COUNT} == ${NUM_QUERIES} ]]
        then
            break
        fi
    done

    while (( $(echo "$(bc -l <<< "${CURRENT}-${PREV}") < ${PERIOD}" | bc -l) ))
    do
        sleep 1s
        CURRENT=$(fraction ${LOG_FILE})
    done

    PREV=${CURRENT}
    FOLDER_NAME=$(echo "${PERIOD} * ${ITERATION}" | bc -l)

    if [[ ${FOLDER_NAME} == "."* ]]
    then
        FOLDER_NAME="0${FOLDER_NAME}"
    fi

    mkdir -p "${OUTPUT_DIR}${FOLDER_NAME}/"
    cp -r "${THETIS_OUTPUT_DIR}"* "${OUTPUT_DIR}${FOLDER_NAME}/"
    ITERATION=$((${ITERATION} + 1))
done

echo
echo "Done executing queries"
echo "You can stop progressive indexing in Thetis now"
