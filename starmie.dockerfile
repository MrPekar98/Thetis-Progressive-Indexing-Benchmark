FROM ubuntu:20.04

WORKDIR /home
RUN apt update
RUN apt install python3 pip git -y
RUN git clone https://github.com/megagonlabs/starmie.git

ADD starmie.sh starmie/
RUN rm starmie/run_pretrain.py starmie/extractVectors.py starmie/test_lsh.py starmie/sdd/pretrain.py
ADD baseline_code/starmie/starmie_pretrain.py starmie/
ADD baseline_code/starmie/extractVectors.py starmie/
ADD baseline_code/starmie/use_lsh.py starmie/
ADD baseline_code/starmie/pretrain.py starmie/sdd/
ADD baseline_code/starmie/requirements.txt starmie/
ADD baseline_code/starmie/ranking.py starmie/
ADD baseline_code/experiment/ starmie/

WORKDIR starmie/
RUN pip3 install -r requirements.txt

ENTRYPOINT ./starmie.sh
