FROM ubuntu:20.04

WORKDIR /home
ADD queries/ /queries
# TODO: Add script to run that can convert the queries from 'queries/' into CSV queries
ADD SemanticTableSearchDataset/table_corpus/csv_tables_2019/ /wikitables
ADD gittables_csv/ /gittables

RUN apt update
RUN apt install python3 pip wget zip openjdk-11-jdk git -y
RUN git clone https://github.com/northeastern-datalab/santos.git

WORKDIR santos/
RUN pip3 install -r requirements.txt
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-class.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-facts.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-full-types.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-labels.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-sameAs.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-schema.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-shapes.nt.gz
RUN wget https://yago-knowledge.org/data/yago4/full/2020-02-24/yago-wd-simple-types.nt.gz
RUN gzip -d *.gz
RUN mv *.nt yago/yago_original/

WORKDIR codes/
RUN python3 preprocess_yago.py
RUN python3 Yago_type_counter.py
RUN python3 Yago_subclass_extractor.py
RUN python3 Yago_subclass_score.py

WORKDIR ../ground_truth/
ADD santos_fd.zip .
RUN unzip santos_fd.zip

WORKDIR santos_fd/
ADD wikitables.txt .
ADD gittables.txt .
RUN ./runFilesWT.sh
RUN python3 sortFDs_pickle_file_dict.py wikitables
RUN mv wikitables_FD_filedict.pickle ..
RUN python3 gen_union.py /queries/5-row/ /wikitables/ wikitables
RUN mv wikitablesUnionBenchmark.pickle ..
RUN python3 gen_intent_columns.py wikitables
RUN mv wikitablesIntentColumnBenchmark.pickle ..
RUN rm -r results/ entity_weights.json
RUN ./runFilesGT.sh
RUN python3 sortFDs_pickle_file_dict.py gittables
RUN mv gittables_FD_filedict.pickle ..
RUN python3 gen_union.py /queries/5-row/ /gittables/ gittables
RUN mv gittablesUnionBenchmark.pickle ..
RUN python3 gen_intent_columns.py gittables
RUN mv gittablesIntentColumnBenchmark.pickle ..

WORKDIR /home/santos/codes
ADD santos.sh .
RUN rm data_lake_processing_yago.py query_santos.py
ADD baseline_code/santos/santos_data_lake_preprocessing_yago.py .
ADD baseline_code/santos/query_santos .
ADD sub_corpus.py .

CMD []
#ENTRYPOINT ./santos.sh
