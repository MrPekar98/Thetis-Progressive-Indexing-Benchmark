#!/bin/bash

set -e

echo "Running D3L ranking experiment"
python ranking.py ${FRACTION} ${FRACTION_LIMIT} ${CORPUS} ${OVERLAP}

echo
echo "Done"
