FROM ubuntu:20.04

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install python3 pip git wget gzip openjdk-11-jdk -y
RUN git clone https://github.com/northeastern-datalab/santos.git

# Adding queries tables
ADD queries/low_overlap_csv/ /queries/low/
ADD queries/high_overlap_csv/ /queries_high/
ADD SemanticTableSearchDataset/table_corpus/csv_tables_2019/ /wikitables/
ADD gittables_csv/ /gittables/

# Preparing KG (YAGO) files
WORKDIR santos/
RUN pip install -r requirements.txt
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-annotated-facts.ntx.gz -O yago/yago_original/yago-wd-annotated-facts.ntx.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-class.nt.gz -O yago/yago_original/yago-wd-class.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-facts.nt.gz -O yago/yago_original/yago-wd-facts.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-full-types.nt.gz -O yago/yago_original/yago-wd-full-types.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-labels.nt.gz -O yago/yago_original/yago-wd-labels.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-sameAs.nt.gz -O yago/yago_original/yago-wd-sameAs.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-schema.nt.gz -O yago/yago_original/yago-wd-schema.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-shapes.nt.gz -O yago/yago_original/yago-wd-shapes.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-simple-types.nt.gz -O yago/yago_original/yago-wd-simple-types.nt.gz

WORKDIR yago/yago_original/
RUN gzip -d *.gz

# Processing YAGO
WORKDIR ../../codes/
RUN python3 preprocess_yago.py
RUN python3 Yago_type_counter.py
RUN python3 Yago_subclass_extractor.py
RUN python3 Yago_subclass_score.py
ADD baseline_code/santos/*.pickle ../groundtruth/

# Adding experiment files
RUN rm data_lake_processing_yago.py data_lake_processing_synthesized_kb.py query_santos.py
ADD baseline_code/experiment/ .
ADD baseline_code/santos/chained_ranking.py .
ADD baseline_code/santos/ranking.py .
ADD baseline_code/santos/query_santos.py .
ADD baseline_code/santos/data_lake_processing_yago.py .
ADD baseline_code/santos/data_lake_processing_synthesized_kb.py .
ADD santos.sh .

ENTRYPOINT ./santos.sh
