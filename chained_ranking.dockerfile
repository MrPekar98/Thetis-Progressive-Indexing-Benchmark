FROM ubuntu:20.04

WORKDIR /home
RUN apt update
RUN apt install python3 pip bc -y
RUN pip install neo4j scikit-learn

ADD chained_ranking.py .
ADD select_result_table.py .
ADD chained_ranking_gt.py .
ADD chained_ndcg.py .
ADD to_query.py .
ADD queries/ initial_queries/

CMD python3 chained_ranking.py
