# Jazero Progressive Indexing Benchmark
A benchmark to evaluate progressive indexing in Jazero.

## Setup
Here, we setup the Jazero data lake and the benchmark for evaluating table search.

### Setting Up Table Search Benchmark
Clone the benchmark repository.

```bash
git clone https://github.com/EDAO-Project/SemanticTableSearchDataset.git
./download_dbpedia.sh SemanticTableSearchDataset/dbpedia_files.txt
```

Run the following list of commands to properly unpack the downloaded benchmark.

```bash
cd SemanticTableSearchDataset/
rm -r ground_truth/2013/ queries/2013/
cd ground_truth/2019/navigational_links/
for F in ./* ; do tar -xf ${F} ; rm ${F} ; mv ${F:0:-7}/* . ; rmdir ${F:0:-7} ; done
cd ../wikipedia_categories/
for F in ./* ; do tar -xf ${F} ; rm ${F} ; mv ${F:0:-7}/* . ; rmdir ${F:0:-7} ; done
cd ../wikipage_to_categories/
tar -xf wikipage_to_categories.tar.gz
rm wikipage_to_categories.tar.gz
cd ../wikipage_to_navigation_links/
for F in ./* ; do tar -xf ${F} ; rm ${F} ; done
```

In this current directory (`ground_truth/2019/wikipage_to_navigation_links/`), execute the following Python script.

```python
import os
import json

files = os.listdir('.')
concat = dict()

for file in files:
    if not '.json' in file:
        continue

    with open(file, 'r') as handle:
        lst = json.load(handle)

        for wikipage in lst.keys():
            concat[wikipage] = lst[wikipage]

with open('wikipage-to-navigational-link.json', 'w') as handle:
    json.dump(concat, handle, indent = 4)
```

Run the following list of commands from the root directory of tghe benchmark directory to unpack the table corpus.

```bash
rm -r table_corpus/*2013*
cd table_corpus/
tar -xf tableIDToEntities_2019.ttl.tar.gz
rm tableIDToEntities_2019.ttl.tar.gz
cd csv_tables_2019/
for F in ./* ; do tar -xf ${F} ; rm ${F} ; mv csv_tables_2019/${F:0:-7}/* . ; done && rm -rf csv_tables_2019
cd ../tables_2019/
for F in ./* ; do tar -xf ${F} ; rm ${F} ; mv tables_2019/${F:0:-7}/* . ; done && rm -r tables_2019/
```

Finally, go back to the root directory of this repository and process the tables to annotate the tables with knowledge graph entity links.

```bash
python format_tables.py
```

### Setting Up Jazero
First, download the Jazero data lake and move the KG into that directory.

```bash
git clone https://github.com/EDAO-Project/Jazero.git
mv kg/ Jazero/
```

Download embeddings to be loaded into Jazero.

```bash
wget -O embeddings.zip https://zenodo.org/records/6384728/files/embeddings.zip?download=1
unzip embeddings.zip
rm embeddings.zip
```

Start a Neo4J instance in which we will load the DBpedia KG.

```bash
mkdir -p neo4j_data/ neo4j_plugins/
docker network create neo4j-network
docker run -d \
    --restart always \
    --network=neo4j-network \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/12345678 \
    --env NEO4J_PLUGINS='["apoc", "n10s"]' \
    --volume=${PWD}/neo4j_data/:/data \
    --volume=${PWD}/neo4j_plugins/:/plugins \
    --volume=${PWD}/Jazero/kg/:/kg \
    --name benchmark_neo4j \
    neo4j:5.5.0
sleep 10s
docker cp import_dbpedia.sh benchmark_neo4j:/var/lib/neo4j
docker exec -it benchmark_neo4j bash -c './import_dbpedia.sh'
```

Generate ground truth entity links by running the following script.

```bash
docker run --rm --network=neo4j-network -it -v ${PWD}:/home python:3.9.19 bash -c "pip install neo4j && python /home/gen_entity_links.py $(docker exec benchmark_neo4j hostname -I)"
docker stop benchmark_neo4j
```

This will create the file `entity-links.json` of entity links for all corpus tables.
Move this `entity-links.json` file to the folder `Jazero/index/`.
Now, replace the file `Jazero/entity-linker/src/main/java/dk/aau/cs/dkwe/edao/jazero/entitylinker/EntityLinker.java` with the file `EntityLinker.java`.

Start Jazero.

```bash
cd Jazero/
./start.sh
```

While Jazero is starting, compile the connector that allows us to communicate with Jazero.

```bash
cd JDLC/c/
mkdir build/ lib/
cd build/
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build ./ --target all -- -j 6
```

Copy the `jdlc_cmd` file into the root directory of this repository.
Run the following commands to set the admin user and to load the KG into Jazero when Jazero is fully booted.

```bash
curl -H "Content-Type: application/json" -d '{"username": "admin", "password": "1234"}' http://localhost:8081/set-admin
docker exec jazero_neo4j /scripts/install.sh
docker restart jazero_neo4j
sleep 10s
docker exec jazero_neo4j /scripts/import.sh . /kg
```

Load Jazero with the embeddings.

```bash
./jdlc_cmd -o insertembeddings -h localhost -u admin -c 1234 -j Jazero/ -e vectors.txt -d ' '
```

## Experiments
TODO: Now, run the experiments with the progressive indexing.
