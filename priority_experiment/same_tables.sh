#!/bin/bash

set -e

POSTGRES_HOST=$(docker exec db hostname -I)
NEO4J_HOST=$(docker exec thetis_neo4j hostname -I)
NETWORK="thetis_network"
