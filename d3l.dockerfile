FROM python:3.7.10

RUN apt update
WORKDIR /d3l/
RUN pip install git+https://github.com/alex-bogatu/d3l
RUN python -m nltk.downloader all

ADD baseline_code/d3l/ .
ADD baseline_code/experiment/ .
ADD d3l.sh .

CMD ./d3l.sh
