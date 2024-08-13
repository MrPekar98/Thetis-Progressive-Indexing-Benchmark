#!/bin/bash

set -e

for QUERY in "different_queries/"* ;\
do
    echo "Executing ${QUERY}"
    cp ${QUERY} ../TableSearch/queries/
    sleep 30s
done
