#!/bin/bash

set -e

for QUERY in "similar_queries/"* ;\
do
    echo "Executing ${QUERY}"
    cp ${QUERY} ../TableSearch/queries/
    sleep 30s
done
