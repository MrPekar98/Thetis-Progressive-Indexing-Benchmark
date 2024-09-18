FROM ubuntu:20.04

RUN apt update
RUN apt install python3 pip -y

ADD santos/ santos/
ADD santos.sh .

ENTRYPOINT ./santos.sh
