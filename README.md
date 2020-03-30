# evtxtologstash
Reads Windows Event Log files and outputs them as json towards Logstash for further processing

Installation
------------
Requires Python3 to run the Python file and the below libraries

```python
pip3 install python-evtx xmltodict python-logstash 
```
As a container
--------------
`docker run --rm -it -v <path_to_evtx_file>:logs.evtx stevengoossens/evtxtologstash bash -c 'python EvtxToLogstash.py logs.evtx <logstash_host> <logstash_port>'`
