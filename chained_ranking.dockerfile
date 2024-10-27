FROM ubuntu:20.04

WORKDIR /home
RUN apt update
RUN apt install python3 pip bc -y
RUN pip install neo4j

ADD chained_ranking.sh .
ADD select_result_table.py .
ADD to_query.py .
ADD queries/ initial_queries/

ENTRYPOINT ./chained_ranking.sh
