FROM ubuntu:20.04

WORKDIR /home
RUN apt update
RUN apt install python3 pip wget zip openjdk-11-jdk -y
ADD santos/ santos/

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

RUN mkdir /ground_truth
WORKDIR /ground_truth
ADD wikitables.txt .
ADD gittables.txt .
ADD santos_fd/ .
RUN ./runFilesWT.sh

WORKDIR /home/santos/codes
ADD santos.sh .
RUN rm data_lake_processing_yago.py query_santos.py
ADD santos_data_lake_preprocessing_yago.py .
ADD query_santos .
ADD sub_corpus.py .

ENTRYPOINT ./santos.sh
