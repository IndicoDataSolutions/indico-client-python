FROM python:3.9.15

COPY . /indico-client
WORKDIR /indico-client
RUN python3 setup.py install
RUN apt-get update && apt-get install python3-sphinx -y 
CMD ["sleep", "infinity"]