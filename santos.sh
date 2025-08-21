#!/bin/bash

set -e

echo "Ranking experiment"
python ranking.py ${FRACTION} ${FRACTION_LIMIT} ${CORPUS} ${OVERLAP}

echo "Chained ranking experiment"
python chained_ranking.py ${FRACTION} ${FRACTION_LIMIT} ${CORPUS} ${OVERLAP}

echo
echo "Done"
