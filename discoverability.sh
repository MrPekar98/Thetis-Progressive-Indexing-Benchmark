#!/bin/bash

set -e

NUM_TABLES=$1
OUTPUT_DIR="results/discoverability/"

mkdir -p ${OUTPUT_DIR}

if [[ ${NUM_TABLES} < 1 ]]
then
    echo "Pass number of tables that is greater than 0"
    exit 1
fi
