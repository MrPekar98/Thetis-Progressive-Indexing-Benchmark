#!/bin/bash

set -e

NUM_TABLES=$1
CORPUS=$2
OUTPUT_DIR="results/discoverability/"
OUTPUT_FILE="${OUTPUT_DIR}discovered_times.txt"
NEW_TABLES_DIR="TableSearch/tables/"
PERIOD=$((10 * 60))
START=$(date +%s)
CURRENT=${START}
END=$((60 * 60))
NEW_TABLES="new_tables/${CORPUS}/"
TMP_NEW_TABLES="new_tables/${CORPUS}_tmp/"
LOG_FILE="TableSearch/data/log.txt"

if [[ ${NUM_TABLES} < 1 ]]
then
    echo "Pass number of tables that is greater than 0"
    exit 1
elif [[ ${CORPUS} != "wikitables" && ${CORPUS} != "gittables" ]]
then
    echo "Corpus must be either 'wikitables' or 'gittables'"
    exit 1
fi

mkdir -p ${OUTPUT_DIR} ${TMP_NEW_TABLES}
echo "Times:" > ${OUTPUT_FILE}
echo "Running experiment..."

TIME_POINT=0
TIME_POINT_TRUE=${START}
INSERTED=0

while [ $((${CURRENT} - ${START})) -le ${END} ]
do
    CURRENT=$(date +%s)

    if [[ $(((${CURRENT} - ${START}) % ${PERIOD})) == 0 ]]
    then
        echo "" > ${LOG_FILE}
        echo "Not found: $(ls ${TMP_NEW_TABLES} | wc -l)/${INSERTED}" >> ${OUTPUT_FILE}
        rm -r ${TMP_NEW_TABLES}
        mkdir ${TMP_NEW_TABLES}

        TIME_POINT=$(((${CURRENT} - ${START}) / 60))
        TIME_POINT_TRUE=${CURRENT}
        INSERTED=0
        echo "Inserting tables at time point ${TIME_POINT}m"
        echo "Time point ${TIME_POINT}m" >> ${OUTPUT_FILE}

        for TABLE in "${NEW_TABLES}"*
        do
            INSERTED=$((${INSERTED} + 1))

            if [[ ${INSERTED} == ${NUM_TABLES} ]]
            then
                break
            fi

            cp ${TABLE} ${TMP_NEW_TABLES}
            cp ${TABLE} ${NEW_TABLES_DIR}
        done

        sleep 1s
    fi

    for TABLE in "${TMP_NEW_TABLES}"*
    do
        TABLE_TOKENS=(${TABLE//// })
        TABLE_ID=${TABLE_TOKENS[-1]}

        if grep -q "${TABLE_ID}" ${LOG_FILE}
        then
            rm ${TABLE}
            echo "${TABLE_ID}: $(((${CURRENT} - ${TIME_POINT_TRUE}) / 60))" >> ${OUTPUT_FILE}
        fi
    done
done

echo "Done"

if [[ ${CORPUS} == "wikitables" ]]
then
    rm "SemanticTableSearchDataset/table_corpus/tables_2019/new"*
elif [[ ${CORPUS} == "gittables" ]]
then
    rm "gittables/new"*
else
    echo "Clean up yourself. The corpus name was not recognized."
    exit 1
fi

rm -r ${TMP_NEW_TABLES}
