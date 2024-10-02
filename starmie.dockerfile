FROM ubuntu:20.04

WORKDIR /home
RUN apt update
RUN apt install python3 pip -y
RUN git clone https://github.com/megagonlabs/starmie.git

ADD starmie.sh .
RUN rm starmie/run_pretrain.py starmie/sdd/pretrain.py
ADD baseline_code/starmie/starmie_pretrain.py starmie/
ADD baseline_code/starmie/pretrain.py starmie/sdd/
ADD baseline_code/starmie/requirements.txt starmie/

WORKDIR starmie/
RUN pip3 install -r requirements.txt

ENTRYPOINT ./starmie.sh
