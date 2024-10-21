#!/bin/bash

set -e

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

PERIOD="1.0"
RESULT_DIR="/results/chained_ranking/"
INITIAL_QUERIES="initial_queries/"
EXP_QUERIES="experiment_queries/"
THETIS_DIR="/TableSearch/"
QUERY_DIR="${THETIS_DIR}queries/"
LOG_FILE="${THETIS_DIR}data/log.txt"
OUTPUT_DIR="${THETIS_DIR}data/output/search_output/"

if [[ ${TYPE} != "low" && ${TYPE} != "high" ]]
then
    echo "Type must be either 'low' or 'high', indicating the result set overlap for the query set"
    exit 1
elif [[ ${CORPUS} != "wikitables" && ${CORPUS} != "gittables" ]]
then
    echo "Corpus must be either 'wikitables' or 'gittables'"
    exit 1
fi

INITIAL_QUERIES="${INITIAL_QUERIES}${TYPE}_overlap/"

mkdir -p ${RESULT_DIR} ${EXP_QUERIES}
cp ${INITIAL_QUERIES}* ${EXP_QUERIES}
sleep 2s

START=$(fraction ${LOG_FILE})
CURRENT=${START}
PREV=${CURRENT}
LIMIT="30.00"
ITERATION=0
NUM_QUERIES=$(ls ${QUERY_DIR} | wc -l)
CORPUS_DIR="/wikitables/"

if [[ ${CORPUS} == "gittables" ]]
then
    CORPUS_DIR="/gittables/"
fi

while [ $(echo "${CURRENT} < ${LIMIT}" | bc -l) ]
do
    ITERATION=$((${ITERATION} + 1))

    # Wait until next period
    while (( $(echo "$(bc -l <<< "${CURRENT}-${PREV}") < ${PERIOD}" | bc -l) ))
    do
        sleep 1s
        CURRENT=$(fraction ${LOG_FILE})
    done

    PREV=${CURRENT}
    mv ${EXP_QUERIES}* ${QUERY_DIR}

    # Wait until all queries have been executed
    EXECUTED=$(ls ${OUTPUT_DIR} | wc -l)
    echo "Executing queries in iteration ${ITERATION} after having indexed ${CURRENT}% of the data"

    while [ ${EXECUTED} -ne ${NUM_QUERIES} ]
    do
        sleep 2s
        EXECUTED=$(ls ${OUTPUT_DIR} | wc -l)
    done

    PROGRESS==$(echo "${PERIOD} * ${ITERATION}" | bc -l)
    mkdir -p "${RESULT_DIR}${PROGRESS}"
    mv ${OUTPUT_DIR}* "${RESULT_DIR}${PROGRESS}"
    echo "Saving results and constructing new queries"

    # Construct new queries
    for RESULT in "${RESULT_DIR}${PROGRESS}"* ;\
    do
        OUTPUT_FILE="null"
        INDEX=0
        RESULT_FILE="${RESULT}filenameToScore.json"

        while [ ! -f ${OUTPUT_FILE} ]
        do
            TABLE_ID=$(python3 select_result_table.py ${RESULT_FILE} ${INDEX})
            TABLE_FILE="${CORPUS_DIR}${TABLE_ID}"
            OUTPUT_FILE="${EXP_QUERIES}${TABLE_ID}"
            INDEX=$((${INDEX} + 1))
            python3 to_query.py ${TABLE_FILE} ${OUTPUT_FILE}

            if [[ ${INDEX} == ${NUM_QUERIES} ]]
            then
                break
            fi
        done
    done
done
