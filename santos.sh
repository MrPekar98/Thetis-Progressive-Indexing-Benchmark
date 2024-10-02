#!/bin/bash

set -e

CURRENT_FRACTION=0.0
SUB_CORPUS="/sub_corpus/"

while [[ ${CURRENT_FRACTION} < ${FRACTION_LIMIT} ]]
do
    echo "Fraction ${CURRENT_FRACTION}/${FRACTION_LIMIT}"

    if [[ -d ${SUB_CORPUS} ]]
    then
        rm -r ${SUB_CORPUS}
    fi

    mkdir ${SUB_CORPUS}
    python3 sub_corpus.py ${SUB_CORPUS}

    python3 santos_data_lake_preprocessing_yago.py ${CORPUS} ${SUB_CORPUS}
    python3 query_santos.py ${CORPUS} ${QUERY_SIZE}

    # TODO: Move results to /results

    CURRENT_FRACTION=$((${CURRENT_FRACTION} + ${FRACTION}))
done

echo
echo "Done"
echo "Evaluating on full corpus"
echo "Indexing..."
python3 santos_data_lake_preprocessing_yago.py ${CORPUS} ${}

echo
echo "Querying..."
python3 query_santos.py ${CORPUS} ${QUERY_SIZE}

echo
echo "Done"
