FROM ubuntu:20.04

WORKDIR /home
RUN apt update
RUN apt install python3 pip -y
RUN pip install numpy vertica_python

ADD MATE/ MATE/
WORKDIR MATE/
RUN rm src/index_generation.py
ADD baseline_code/mate/index_generation.py src/

# When running a container of this image, pass the environment VERTICA=$(docker exec vertica_cs bash -c "hostname -I")
CMD []
