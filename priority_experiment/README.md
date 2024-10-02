# Small Experiments to Analyze Priority Assignment Rules
These experiments analyze the priority assignment rules by running 3 different experiments:
(1) when no queries are executed,
(2) when different queries are executed,
(3) when similar queries for the same tables are executed.

Before running any experiment, remove the indexes from disk and the logging file and then start Jazero.
The index files are 'Jazero/index/*.ser' and the logging file is 'Jazero/logs/log.txt'.

## Setup
In order to analyze the priority assignments, we need to inject logging points into the code.
Therefore, insert the following statements in their respective code locations from the `TableSearch/Thetis/src/main/java/com/thetis/` directory:

- `commands/ProgressiveIndexing.java: 303` `indexWriter.updateIndexable(res.getFirst(), i -> Logger.logNewLine(Logger.Level.INFO, "Event 2 -> ID-" + res.getFirst() + "-" + i));`
- `commands/ProgressiveIndexing.java: 234`: `Logger.setPrintStream(System.out);`
- `commands/ProgressiveIndexing.java: 230`: `Logger.setPrintStream(new PrintStream(new FileOutputStream("/data/log.txt")));`
- `commands/ProgressiveIndexing.java: 24`: `import java.io.PrintStream;`
- `commands/ProgressiveIndexing.java: 25`: `import java.io.FileOutputStream;`
- `loader/progressive/ProgressiveIndexWriter.java: 244`: `Logger.logNewLine(Logger.Level.INFO, "Event 3 -> ID-" + tableToIndex.getId() + "-" + tableToIndex.getPriority());`
- `loader/progressive/ProgressiveIndexWriter.java: 82`: `Logger.logNewLine(Logger.Level.INFO, "Event 1 -> ID-" + item.getId() + "-" + item.getPriority() + "-" + item.getIndexable().rows.size() + "/" + item.getIndexable().numDataRows);`

## Experiment
Here, we run the different experiments and plot the results.

Before running any experiments, delete the logging file `TableSearch/data/log.txt` and all of the previous results `TableSearch/data/search_output/`.
Run the following commands to start progressive indexing.

```bash
cd ../TableSearch/
mkdir queries/
docker run -v $(pwd)/queries:/queries -v $(pwd)/tables:/tables \
    -v $(pwd)/Thetis:/src -v $(pwd)/data:/data \
    -v $(pwd)/../priority_experiment/corpus:/corpus \
    --network thetis_network -e NEO4J_HOST=$(docker exec thetis_neo4j hostname -I) \
    -it --rm thetis bash

# From within the Docker container
cd src/
mvn package -DskipTests
java -Xms25g -jar target/Thetis.0.1.jar progressive -topK 10 -prop types \
    --table-dir /corpus/ --output-dir /home --result-dir /data \
    --indexing-time 1 --singleColumnPerQueryEntity --adjustedSimilarity --useMaxSimilarityPerColumn \
    -nuri "bolt://${NEO4J_HOST}:7687" -nuser neo4j -npassword admin
```

### No Queries
1. Run the commands to start progressive indexing.

2. Run the following commands to extract plotting values once the indexing has completed.

    ```bash
        mv ../TableSearch/data/log.txt log_no_queries.txt
        python plot.py log_no_queries.txt
    ```

    This script will output the data values to plot the experiment results as well as how to plot them.

### Different Queries
1. Run the commands to start progressive indexing.

2. Run the following command in another window immediately to start querying the system.

    ```bash
        ./different_tables.sh
    ```

3. Plot the results.

    ```bash
        mv ../TableSearch/data/log.txt log_different_tables.txt
        python plot.py log_different_tables.txt
    ```

### Similar Queries
1. Run the commands to start progressive indexing.

2. Run the following command in another window immediately to start querying the system.

    ```bash
        ./same_tables.sh
    ```

3. Plot the results.

    ```bash
        mv ../TableSearch/data/log.txt log_same_tables.txt
        python plot.py log_same_tables.txt
    ```

### Meausure Ranking Quality
We measure the ranking quality of Thetis during progressive indexing by executing queries at different time points and compare the rankings to the raning when the indexes are fully constructed.
This experiment consists of two sub-experiments: when executing 10 different queries and 10 similar/same queries.

1. Run the above commands to start progressive indexing.

2. Run the following command in another window immediately to start querying the system using different queries

    ```bash
        ./ranking_different_queries.sh
    ```

    or the following command for similar/same queries.

    ```bash
        ./ranking_different_queries.sh
    ```

3. Plot the results when querying the system with different queries

    ```bash
        python plot_ranking.py different_results/
    ```

    or using similar/same queries.

    ```bash
        python plot_ranking.py similar_queries/
    ```

The files containing the plotting data can be found in `plots_data/`.
