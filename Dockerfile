FROM python:3

ADD EvtxToLogstash.py /

RUN pip3 install python-evtx xmltodict python-logstash 

RUN chmod +x EvtxToLogstash.py
