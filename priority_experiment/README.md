# Small Experiments to Analyze Priority Assignment Rules
These experiments analyze the priority assignment rules by running 3 different experiments:
(1) when no queries are executed,
(2) when different queries are executed, and
(3) when similar queries for the same tables are executed.

Before running any experiment, remove the indexes from disk and the logging file and then start Jazero.
The index files are 'Jazero/index/*.ser' and the logging file is 'Jazero/logs/log.txt'.

## Setup

### Injecting Priority Assignment Logging Points
In order to analyze the priority assignments, we need to inject logging points into the code.
Therefore, insert the following statement after line 80 in 'Jazero/data-lake/src/main/java/dk/aau/cs/dkwe/edao/jazero/datalake/loader/progressive/ProgressiveIndexWriter.java':

'''java
Logger.log(Logger.Level.INFO, "ID-" + item.getId() + "-" + item.getPriority());
'''

## Experiment
Here, we run the different experiments and plot the results.

Before running any experiments, delete the Jazero indexes from disk as well as the logging file.

'''bash
rm Jazero/index/*.ser Jazero/logs/log.txt
'''

Now, start Jazero.
When an experiment terminates, shut down Jazero and repeat the above steps.

### No Queries
This experiment requires no script, so just wait until Jazero completes the indexing.
When Jazero has completed indexing, stop Jazero and run the following command to extract plotting values.

'''python
python plot.py
'''

This script will output the data values to plot the experiment results as well as how to plot them.

### Different Queries
Run the following command to run this experiment when Jazero is fully booted.

'''bash
different_tables.sh
'''

Stop Jazero, and use the following command to plot the results.

'''python
python plot.py
'''

### Similar Queries
Run the following command to run this experiment.

'''bash
same_tables.sh
'''

Stop Jazero, and use the following command to plot the results.

'''python
python plot.py
'''
