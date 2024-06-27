# Jazero Progressive Indexing Benchmark
A benchmark to evaluate progressive indexing in Jazero.

TODO: Pack all of this into a setup Docker file.

## Setup
Here, we setup the Jazero data lake and the benchmark for evaluating table search.

### Setting Up Jazero
First, download the Jazero data lake.

```bash
git clone https://github.com/EDAO-Project/Jazero.git
```

Download embeddings to be loaded into Jazero.

```bash
wget -O embeddings.zip https://zenodo.org/records/6384728/files/embeddings.zip?download=1
unzip embeddings.zip
rm embeddings.zip
```

Download DBpedia.

```bash
./download_dbpedia.sh SemanticTableSearchDataset/dbpedia_files.txt
```

TODO: Add here the instructions to substitute the entity linker.

Start Jazero.

```bash
cd Jazero/
./start.sh
```

While Jazero is started, compile the connector that allows us to communicate with Jazero.

```bash
cd JDLC/c/
mkdir build/ lib/
cd build/
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build ./ --target all -- -j 6
```

Copy the `jdlc_cmd` file into the root directory.
Run the following commands to set the admin user and to load the KG into Jazero.

```bash
curl -H "Content-Type: application/json" -d '{"username": "admin", "password": "1234"}' http://localhost:8081/set-admin
docker exec jazero_neo4j /scripts/install.sh
docker restart jazero_neo4j
sleep 10s
docker exec jazero_neo4j /scripts/import.sh . /kg
```

### Setting Up Table Search Benchmark
Download the benchmark for semantic table search.

```bash
git clone https://github.com/EDAO-Project/SemanticTableSearchDataset.git
```

Run the following list of commands to properly unpack the downloaded benchmark.

```bash
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

Run the following list of commands from the root directory to unpack the table corpus.

```bash
rm -r table_corpus/*2013*
tar -xf tableIDToEntities_2019.ttl.tar.gz
rm tableIDToEntities_2019.ttl.tar.gz
cd csv_tables_2019/
for F in ./* ; do tar -xf ${F} ; rm ${F} ; mv csv_tables_2019/${F:0:-7}/* . ; done && rm -rf csv_tables_2019
cd ../tables_2019/
for F in ./* ; do tar -xf ${F} ; rm ${F} ; mv ${F:0:-7}/* . ; rmdir ${F:0:-7} ; done
```

Finally, process the tables to annotate the tables with knowledge graph entity links.

```bash
python format_tables.py
```
