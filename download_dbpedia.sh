#!/bin/bash

set -e

KG_LIST_FILE=$1
KG_DIR="Jazero/kg/"

if [ ! -f ${KG_LIST_FILE} ]
then
    echo "'${KG_LIST_FILE}' does not exist"
    exit 1
fi

mkdir -p ${KG_DIR}
echo "Downloading files"

while read -r LINE ;
do
    wget -P ${KG_DIR} ${LINE}
done < ${KG_LIST_FILE}

echo
echo "Decompressing files"
for KG_FILE in ${KG_DIR}* ;\
do
    bzip2 -dk ${KG_FILE}
    rm ${KG_FILE}
done

echo "Done"
