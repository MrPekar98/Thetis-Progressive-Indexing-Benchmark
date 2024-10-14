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
cd ground_truth/2019/navigation_links/
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

Run the following list of commands from the root directory of the benchmark directory to unpack the table corpus.

```bash
rm -r table_corpus/*2013*
cd table_corpus/
cd csv_tables_2019/
for F in ./* ; do tar -xf ${F} ; rm ${F} ; mv csv_tables_2019/${F:0:-7}/* . ; done && rm -rf csv_tables_2019
cd ../tables_2019/
for F in ./* ; do tar -xf ${F} ; rm ${F} ; mv tables_2019/${F:0:-7}/* . ; done && rm -r tables_2019/
```

We now also add the GitTabes dataset, which consists of more tables (1M) of more rows (142 on average per table).
Download the dataset with the following commands:

```bash
mkdir -p gittables/
wget -O gittables.zip https://zenodo.org/api/records/6517052/files-archive
unzip gittables.zip
rm gittables.zip
mv *.zip gittables/
python format_gittables.py
python json2csv.py gittables/
```

### Setting Up Thetis
First, clone the Thetis repository from the repository root directory.

```bash
git clone https://github.com/EDAO-Project/TableSearch.git
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
    --name db -d postgres:12.15
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

From within the Thetis container, run the following command to start loading the embeddings.

```bash
cd src/
mvn package -DskipTests
java -jar target/Thetis.0.1.jar embedding \
    -f /data/embeddings/vectors.txt \
    -db postgres -h ${POSTGRES_HOST} \
    -p 5432 -dbn embeddings -u admin -pw 1234 -dp
```

You can now exit the Thetis Docker container with `Ctrl+D` and go back to the repository root directory.

Finally, insert the following code:

- `TableSearch/Thetis/src/main/java/com/thetis/commands/ProgressiveIndexing.java: 195`:
```java
try
{
    Configuration.setLogLevel(Logger.Level.DEBUG);
    Logger.setPrintStream(new PrintStream(new FileOutputStream("/data/log.txt")));
}

catch (FileNotFoundException ignored) {}
```
- `TableSearch/Thetis/src/main/java/com/thetis/commands/ProgressiveIndexing.java: 24`:
```java
import com.thetis.system.Configuration;
import java.io.PrintStream;
import java.io.FileOutputStream;
import java.io.FileNotFoundException;
```

### Setting Up SANTOS
<a href="https://github.com/northeastern-datalab/santos">SANTOS</a> is a semantic table union search approach.
Clone the repository and build the Docker image:

```bash
docker build -t santos -f santos.dockerfile .
```

Unzip `santos_fd.zip`:

```bash
unzip santos_fd.zip
```

### Setting Up Starmie
<a href="https://github.com/megagonlabs/starmie">Starmie</a> is an approach for semantic data discovery based on learned column representations.
Clone the repository and build the Docker image:

```bash
docker build -t starmie -f starmie.dockerfile .
```

## Experiments
Run the following command to create the set of queries for the experiments, and pass the number of queries you wish to use in the experiments:

```bash
python gen_queries.py <number of queries>
```

In an independent window, run a Docker container and start progressively indexing Thetis:

```bash
cd TableSearch/
WT="../SemanticTableSearchDataset/table_corpus/tables_2019/"
GT="../gittables/"
mkdir -p queries/ tables/ data/output/ data/indexes/
docker run -v $(pwd)/queries:/queries \
           -v $(pwd)/tables:/tables \
           -v $(pwd)/Thetis:/src -v $(pwd)/data:/data \
           -v $(pwd)/${WT}:/corpus \
           --network thetis_network -e NEO4J_HOST=$(docker exec thetis_neo4j hostname -I) \
           -it --rm thetis bash
```

This will now set the corpus to Wikitables.
To use GitTables, substitute the variable `${WT}` in the Docker command with `${GT}`.

Then, start progressive indexing using types within the Docker container:

```bash
WT_ROWS=10956092
GT_ROWS=67774304
cd src/
mvn package -DskipTests
java -Xms25g -jar target/Thetis.0.1.jar progressive -topK 100 -prop types \
     --table-dir /corpus/ --output-dir /data/indexes/ --result-dir /data/ \
     --indexing-time 0 --singleColumnPerQueryEntity --adjustedSimilarity --useMaxSimilarityPerColumn \
     -pf HNSW -nuri "bolt://${NEO4J_HOST}:7687" -nuser neo4j -npassword admin -tr ${WT_ROWS}
```

Alternatively, start progressive indexing using embeddings:

```bash
WT_ROWS=10956092
GT_ROWS=67774304
cd src/
mvn package -DskipTests
java -Xms25g -jar target/Thetis.0.1.jar progressive -topK 100 -prop embeddings --embeddingSimilarityFunction abs_cos \
     --table-dir /corpus/ --output-dir /data/indexes/ --result-dir /data/output/ \
     --indexing-time 0 --singleColumnPerQueryEntity --adjustedSimilarity --useMaxSimilarityPerColumn \
     -pf HNSW -nuri "bolt://${NEO4J_HOST}:7687" -nuser neo4j -npassword admin -tr ${WT_ROWS}
```

Once again, if GitTables are used as the corpus, substitute the variable `${WT_SIZE}` with `${GT_SIZE}`.

### Table Discoverability
In this experiment, we evaluate how long it takes before a new table that is inserted into the corpus during indexing becomes discoverable.
Specifically, we insert a fixed number of tables at fixed time points and measure how long it takes for the newly inserted table to become retrievable.
The number of tables to insert is a parameter.

Run the above commands to start progressive indexing, and immediately start the following script, and pass the name of the corpus (`wikitables` or `gittables`).

```bash
touch TableSearch/data/log.txt
python discoverability.py <NUMBER_OF_TABLES> <CORPUS>
```

Note that there is a total of 1000 tables to insert.
The results are stored in `results/discoverability/discovered_times.txt`.

### Ranking Quality
We measure the ranking quality using NDCG during the early stages of progressive indexing.
This evaluates the ranking quality when the time-to-insight is significantly reduced.
Specifically, we focus on querying the baselines in the very early stages of progressive indexing.

#### Thetis
Start progressive indexing in Thetis, as described above, and run immediately the following script to start the experiment.
Pass a period in fractions that indicates how much data to index until we execute queries again.
Pass also the number of queries to execute at every time point.
Note that the resource comes with more than 2K queries for this corpus, by we suggest you use a much smaller number of queries, e.g., 10.

```bash
./ranking.sh <PERIOD> <NUM_QUERIES>
```

The results are stored in `results/ranking/`.

Before evaluating ranking, the ground truth must be established.
Copy the same number of queries to the `TableSearch/queries/` directory with the following script:

```bash
COUNT=0

for QUERY in "SemanticTableSearchDataset/queries/2019/1_tuples_per_query/"* ;\
do
    COUNT=$((${COUNT} + 1))
    cp ${QUERY} TableSearch/queries/

    if [[ ${COUNT} == "<INSERT NUMBER OF QUERIES HERE>" ]]
    then
        break
    fi
done
```

Construct then indexes by running the following script within the Thetis Docker container:

```bash
java -Xms25g -jar target/Thetis.0.1.jar index --table-dir /corpus/ \
     --output-dir /data/indexes/ -t 4 -nuri "bolt://${NEO4J_HOST}:7687" -nuser neo4j -npassword admin
```

Run the following script to perform searching in Thetis.

```bash
RESULT_DIR="/data/ground_truth/"
mkdir -p ${RESULT_DIR}

java -Xms25g -jar target/Thetis.0.1.jar search -prop embeddings -topK 10 \
     -q /queries/ -td /corpus/ -i /data/indexes/ -od ${RESULT_DIR} --embeddingSimilarityFunction abs_cos \
     --singleColumnPerQueryEntity --adjustedSimilarity --useMaxSimilarityPerColumn -pf HNSW \
     -nuri "bolt://${NEO4J_HOST}:7687" -nuser neo4j -npassword admin
```

Now, evaluate the ranking using NDCG by running the Python script:

```bash
mkdir -p results/ground_truth/
cp -r TableSearch/data/ground_truth/search_output/* results/ground_truth/
python ndcg.py
```

The results are now stored in `ndcg.txt`.

#### SANTOS
We perform an experiment to evaluate the ranking using SANTOS during progressive and adaptive indexing.
We incrementally add more data to index based on the same priority assignment rules applied in Thetis.

The ranking experiment in SANTOS is already set up in a Docker images.
To run the experiment, run the Docker container, and pass the fraction of data to index in between query executions, the maximum fraction of data to index before concluding the experiment, pass 1 or 5 for the number of rows for the queries, and the name of the corpus to evaluate on (must be either `wikitables` or `gittables`):

```bash
mkdir -p santos_results/
docker run --rm -v ${PWD}/santos_results:/results \
           -e FRACTION=<insert fraction> \
           -e FRACTION_LIMIT=<insert limit> \
           -e QUERY_SIZE=<insert query size> \
           -e CORPUS=<insert corpus name> santos
```

The results can now be found in `santos_results/`.
Now some plotting...

#### Starmie
We perform the same experiment in Starmie as with SANTOS, and the experiment is also aldready setup in a Docker images.
Run the experiment with the following commands, and pass the fraction of data to index in between query executions, the maximum fraction of data to index before concluding the experiment, the pass 1 or 5 for the number of rows for the queries, and the name of the corpus to evaluate on (must be either `wikitables` or `gittables`):

```bash
mkdir -p starmie_results/
docker run --rm -v ${PWD}/starmie_results:/results \
           -v  ${PWD}/SemanticTableSearchDataset/table_corpus/csv_tables_2019:/wikitables\
           -v ${PWD}/gittables_csv:/gittables \
           -v ${PWD}/queries:/queries \
           -e FRACTION=<insert period> \
           -e FRACTION_LIMIT=<insert limit> \
           -e QUERY_SIZE=<insert query size> \
           -e CORPUS=<insert corpus name> starmie
```

The results can now be found in `starmie_results/`.
Now some plotting...
