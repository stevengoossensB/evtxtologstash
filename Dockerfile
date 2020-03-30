FROM python:3

ADD EvtxToLogstash.py /

RUN pip3 install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org python-evtx xmltodict python-logstash 

RUN chmod +x EvtxToLogstash.py
