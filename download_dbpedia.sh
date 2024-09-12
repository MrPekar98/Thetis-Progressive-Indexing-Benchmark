#!/bin/bash

set -e

if [ "$#" -ne 1 ]
then
    echo "Expected file with list of download URLs"
    exit 1
fi

FILE=$1
OUT_DIR="files/"

mkdir -p ${OUT_DIR}
echo "Download files"

while read -r line; do
    [[ "$line" =~ ^#.*$ ]] && continue

    wget -P ${OUT_DIR}/ $line
    bzip2 -dk ${OUT_DIR}/${line##*/}
    filename=$(basename -- "${OUT_DIR}/${line##*/}")
    filename="${filename%.*}"
done < ${FILE}

rm ${OUT_DIR}*.bz2

if [ -f ${OUT_DIR}/'wikipedia-links_lang=en.ttl' ]
then
    echo "Cleaning 'wikipedia-links_lang=en.ttl'"
    grep --color=never -F 'isPrimaryTopicOf' ${OUT_DIR}/'wikipedia-links_lang=en.ttl' > ${OUT_DIR}/'parsed-wikipedia-links_lang=en.ttl'
    rm -v ${OUT_DIR}/'wikipedia-links_lang=en.ttl'
fi
