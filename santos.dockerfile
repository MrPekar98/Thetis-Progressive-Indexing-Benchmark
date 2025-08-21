FROM ubuntu:20.04

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install python3 pip git wget zip openjdk-11-jdk -y
RUN git clone https://github.com/northeastern-datalab/santos.git

# Adding queries tables
ADD queries/low_overlap_csv/ /queries/low/
ADD queries/high_overlap_csv/ /queries_high/
ADD SemanticTableSearchDataset/table_corpus/csv_tables_2019/ /wikitables/
ADD gittables_csv/ /gittables/

# Preparing KG (YAGO) files
WORKDIR santos/
RUN pip install -r requirements.txt
RUN wget https://yago-knowledge.org/data/yago4.5/yago-4.5.0.2.zip -O yago/yago_original/yago.zip
RUN unzip yago/yago_original/yago.zip -d yago/yago_original/
RUN rm yago/yago_original/yago.zip

# Constructing ground truth
WORKDIR groundtruth/gen/
ADD wikitables.txt .
ADD gittables.txt .
ADD baseline_code/santos/runFilesWikitables.sh .
ADD baseline_code/santos/runFilesGittables.sh .
ADD baseline_code/santos/sortFDs_pickle_file_dict.py .
ADD baseline_code/santos/*.jar .
RUN ./runFilesWikitables.sh
RUN ./runFilesGittables.sh
RUN python3 sortFDs_pickle_file_dict.py wikitables
RUN python3 sortFDs_pickle_file_dict.py gittables
RUN mv wikitabels_FD_filedict.pickle ..
RUN mv gittables_FD_filedict.pickle ..

# Adding experiment files
WORKDIR ../../codes/
RUN rm data_lake_processing_yago.py data_lake_processing_synthesized_kb.py query_santos.py
ADD baseline_code/experiment/ .
ADD baseline_code/santos/ .
RUN rm runFilesWikitables.sh runFilesGittables.sh sortFDs_pickle_file_dict.py gen_union.py *.jar

ENTRYPOINT ./santos.sh
