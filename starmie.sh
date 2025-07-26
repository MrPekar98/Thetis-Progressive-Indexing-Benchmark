#!/bin/bash

set -e

echo "Running Starmie ranking experiment"
python3 ranking.py ${FRACTION} ${FRACTION_LIMIT} ${CORPUS} ${OVERLAP}

echo
echo "Done"
