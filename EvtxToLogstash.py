import contextlib
import mmap
import traceback
import json
import argparse
from collections import OrderedDict
from datetime import datetime

from Evtx.Evtx import FileHeader
from Evtx.Views import evtx_file_xml_view
import xmltodict
import sys
import logging
import logstash


class EvtxToLogstash:
    @staticmethod
    def evtx_to_logstash(filename, logstash_host, port):

        #Create logstash logger to send json strings to
        logger = logging.getLogger('python-logstash-logger')
        logger.setLevel(logging.INFO)
        logger.addHandler(logstash.LogstashHandler(logstash_host, port, version=1))
        
        with open(filename) as infile:
            with contextlib.closing(mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ)) as buf:
                fh = FileHeader(buf, 0x0)
                data = ""
                for xml, record in evtx_file_xml_view(fh):
                    try:
                        contains_event_data = False
                        log_line = xmltodict.parse(xml)

                        # Format the date field
                        date = log_line.get("Event").get("System").get("TimeCreated").get("@SystemTime")
                        if "." not in str(date):
                            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        else:
                            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                        log_line['@timestamp'] = str(date.isoformat())
                        log_line["Event"]["System"]["TimeCreated"]["@SystemTime"] = str(date.isoformat())

                        # Process the data field to be searchable
                        data = ""
                        if log_line.get("Event") is not None:
                            data = log_line.get("Event")
                            if log_line.get("Event").get("EventData") is not None:
                                data = log_line.get("Event").get("EventData")
                                if log_line.get("Event").get("EventData").get("Data") is not None:
                                    data = log_line.get("Event").get("EventData").get("Data")
                                    if isinstance(data, list):
                                        contains_event_data = True
                                        data_vals = {}
                                        for dataitem in data:
                                            try:
                                                if dataitem.get("@Name") is not None:
                                                    data_vals[str(dataitem.get("@Name"))] = str(
                                                        str(dataitem.get("#text")))
                                            except:
                                                pass
                                        log_line["Event"]["EventData"]["Data"] = data_vals
                                    else:
                                        if isinstance(data, OrderedDict):
                                            log_line["Event"]["EventData"]["RawData"] = json.dumps(data)
                                        else:
                                            log_line["Event"]["EventData"]["RawData"] = str(data)
                                        del log_line["Event"]["EventData"]["Data"]
                                else:
                                    if isinstance(data, OrderedDict):
                                        log_line["Event"]["RawData"] = json.dumps(data)
                                    else:
                                        log_line["Event"]["RawData"] = str(data)
                                    del log_line["Event"]["EventData"]
                            else:
                                if isinstance(data, OrderedDict):
                                    log_line = dict(data)
                                else:
                                    log_line["RawData"] = str(data)
                                    del log_line["Event"]
                        else:
                            pass

                        event_data = json.loads(json.dumps(log_line))
                        #print(json.dumps(log_line))
                        logger.info(json.dumps(log_line))


                    except:
                        print("***********")
                        print("Parsing Exception")
                        print(traceback.print_exc())
                        print(json.dumps(log_line, indent=2))
                        print("***********")


if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('evtxfile', help="Evtx file to parse")
    parser.add_argument('logstash_ip', help="IP of logstash")
    parser.add_argument('logstash_port',help='Port for logstash')
    # Parse arguments and call evtx to elk class
    args = parser.parse_args()
    EvtxToLogstash.evtx_to_logstash(args.evtxfile,args.logstash_ip,int(args.logstash_port))
