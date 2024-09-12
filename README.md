# Jazero Progressive Indexing Benchmark
A benchmark to evaluate progressive indexing in Jazero.

## Setup
Here, we setup Thetis and the benchmark for evaluating table search.

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

### Setting up Thetis
First, clone the Thetis repository.

```bash
git clone https://github.com/EDAO-Project/TableSearch.git
```

Download DBpedia 2021.

```bash
./TableSearch/data/kg/dbpedia/download-dbpedia.sh TableSearch/data/kg/dbpedia/dbpedia_files.txt
```

Pull the Neo4J Docker images, create a network for the experiments, and start a container.

```bash
docker pull neo4j:4.1.4
docker network create thetis_network
docker run -d -p 7474:7474 -p 7687:7687 \
    --network thetis_network --name thetis_neo4j \
    -v ${PWD}/files:/kg \
    -e NEO4J_AUTH=none \
    -e NEO4JLABS_PLUGINS='[\"apoc\", \"n10s\"]' \
    -e NEO4J_dbms_security_procedures_unrestricted=apoc.* \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_use_neo4j_config=false \
    neo4j:4.1.4
```

Install Neosemantics.

```bash
docker exec thetis_neo4j wget -P plugins/ https://github.com/neo4j-labs/neosemantics/releases/download/4.1.0.1/neosemantics-4.1.0.1.jar
docker exec thetis_neo4j bash -c "echo 'dbms.unmanaged_extension_classes=n10s.endpoint=/rdf' >> conf/neo4j.conf"
docker restart thetis_neo4j
```

Once Neo4J has completed restarting, load the KG.

```bash
docker cp load.sh thetis_neo4j:/var/lib/neo4j
docker exec thetis_neo4j bash -c "./load.sh /var/lib/neo4j /var/lib/neo4j/import"
```

Download RDF2Vec embeddings for DBpedia 2021.

```bash
wget -O embeddings.zip https://zenodo.org/records/6384728/files/embeddings.zip?download=1
unzip embeddings.zip
rm embeddings.zip
mv vectors.txt TableSearch/data/embeddings/
```

Load the embeddings into Postgres through Thetis.
Next, we will load the embeddings into Postgres through Thetis.
First, start an instance of Postgres.

```bash
docker pull postgres:12.15
docker run --network thetis_network \
    -e POSTGRES_USER=admin \
    -e POSTGRES_PASSWORD=1234 \
    -e POSTGRES_DB=embeddings \
    --name db -d postgres
```

Now, enter the `TableSearch/` directory and start a Docker container with Thetis.

```bash
docker build -t thetis .
docker run --rm -it -v $(pwd)/Thetis:/src \
    -v $(pwd)/data:/data \
    --network thetis_network \
    -e POSTGRES_HOST=$(docker exec db hostname -I) \
    thetis bash
```

Fro within the Thetis container, run the following command to start loading the embeddings.

```bash
cd src/
mvn package -DskipTests
java -jar target/Thetis.0.1.jar embedding \
    -f /data/embeddings/vectors.txt \
    -db postgres -h ${POSTGRES_HOST} \
    -p 5432 -dbn embeddings -u admin -pw 1234 -dp
```

You can now exit the Thetis Docker container with `Ctrl+D` and go back to the repository root directory.

## Experiments
In an independent window, run a Docker container and start progressively indexing Thetis:

```bash
cd TableSearch/
mkdir -p queries/ tables/ data/output/ data/indexes/
docker run -v $(pwd)/queries:/queries \
           -v $(pwd)/tables:/tables \
           -v $(pwd)/Thetis:/src -v $(pwd)/data:/data \
           -v $(pwd)/../SemanticTableSearchDatasettable_corpus/tables_2019:/corpus \
           --network thetis_network -e NEO4J_HOST=$(docker exec thetis_neo4j hostname -I) \
           -it --rm thetis bash
```

Then, start progressive indexing using types:

```bash
cd src/
mvn package -DskipTests
java -Xms25g -jar target/Thetis.0.1.jar progressive -topK 10 -prop types \
     --table-dir /corpus/ --output-dir /data/indexes/ --result-dir /data/output/ \
     --indexing-time 0 --singleColumnPerQueryEntity --adjustedSimilarity --useMaxSimilarityPerColumn \
     -nuri "bolt://${NEO4J_HOST}:7687" -nuser neo4j -npassword admin
```

Alternatively, start progressive indexing using embeddings:

```bash
cd src/
mvn package -DskipTests
java -Xms25g -jar target/Thetis.0.1.jar progressive -topK 10 -prop embeddings --embeddingSimilarityFunction abs_cos \
     --table-dir /corpus/ --output-dir /data/indexes/ --result-dir /data/output/ \
     --indexing-time 0 --singleColumnPerQueryEntity --adjustedSimilarity --useMaxSimilarityPerColumn \
     -nuri "bolt://${NEO4J_HOST}:7687" -nuser neo4j -npassword admin
```

### Table Discoverability
In this experiment, we evaluate how long it takes before a table that is inserted into the corpus becomes discoverable.
Specifically, we insert a fixed number of tables at fixed time points and measure how long it takes for the newly inserted table to become retrievable.
The number of tables to insert is a parameter.

Run the above commands to start progressive indexing, and immediately start the following script and pass the number of tables to insert into the corpus.

```bash
./discoverability.sh <NUM_TABLES>
```

The results are stored in `results/discoverability/`.

### Ranking Quality
We measure the ranking quality using NDCG during the early stages of progressive indexing.
This evaluates the ranking quality when the time-to-insight is significantly reduced.
Specifically, we focus on querying Thetis in the very early stages of progressive indexing.

Start progressive indexing in Thetis, as described above, and run immediately the following script to start the experiment.
Pass a period in seconds that indicates how long to wait until we execute a query again.
Pass also the number of queries to execute at every time point.
Note that the resource comes with more than 2K queries for this corpus, by we suggest you use a much smaller number of queries, e.g., 3.

```bash
./ranking.sh <PERIOD> <NUM_QUERIES>
```

The results are stored in `results/ranking/`.
