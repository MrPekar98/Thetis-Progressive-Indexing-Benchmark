#!/bin/bash

set -e

#echo "Ranking experiment"
#python3 ranking.py ${FRACTION} ${FRACTION_LIMIT} ${CORPUS} ${OVERLAP}

echo "Chained ranking experiment"
python3 chained_ranking.py ${FRACTION} ${FRACTION_LIMIT} ${CORPUS} ${OVERLAP}

echo
echo "Done"
