FROM ubuntu:20.04

RUN apt update
RUN apt install python3 pip -y

ADD starmie/ starmie/
ADD starmie.sh .

ENTRYPOINT ./starmie.sh
