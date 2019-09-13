#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtcdb
from time import gmtime,strftime
from datetime import datetime,timedelta
import time

rtcresponse = {
    'rtcResult' : "OK",
    'rtcIP' : "192.168.22.10",
    'UMB' : {'UMB_internalIp': '192.168.22.10', 'UMB_externalIp': '194.16.1.242', 'UMB_destination': 'routing.egs.samsungallstore.com', 'UMB_datetime': '2018-09-18T18:35:39.465Z', 'UMB_category': 'Command and Control'},
    'AMP' : {'AMP_hash': 'd5221f6847978682234cb8ebfa951cb56b1323658679a820b168bbc1f5261a3b', 'AMP_connector_guid': '20b35f65-9541-447f-ba28-6272c9c4d533', 'AMP_date': '2018-09-18T15:32:21+00:00', 'AMP_hostname': 'contractor', 'AMP_MAC': {0: '00:50:56:ad:27:6f', 1: '02:00:4c:4f:4f:50', 2: '00:05:9a:3c:7a:00'}, 'AMP_IP': {0: '192.168.22.10', 1: '169.254.229.34', 2: '198.19.40.51'}},
    'SW' : {'SW_first_active': '2018-09-18T09:55:00.000+0000', 'SW_last_active': '2018-09-18T12:20:00.000+0000', 'SW_source_IP': '192.168.22.10', 'SW_source_port': 0, 'SW_source_protocol': 'hopopt', 'SW_destination_IP': '0.0.0.0', 'SW_destination_port': 0, 'SW_destination_protocol': 'hopopt', 'SW_security_event_ID': 40}
}

def exception_info(err):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
    return estring

def main(argv):

#
    try:
        mydb = rtcdb.RTCDB()
#        print(str(mydb))
#        mydb.reset_db()
        print("have reset db")
        eventstring = json.dumps(rtcresponse)
        print("eventstring in db is " + eventstring)
        mydb.insertRTCevent(eventstring)
        days = 1
        hours = 1
        fromdate = (datetime.utcnow() - timedelta(days=int(days),hours = int(hours))).strftime('%Y-%m-%d %H:%M:%S')
        
        rsp = mydb.getRTCevent(rtcid=10,fromdate=fromdate)
        print(json.dumps(rsp,indent=4,sort_keys=True))
        
    except Exception as err:
        temp = exception_info(err)
        print("bajssss")
        print(temp)


if __name__ == "__main__":
    main(sys.argv[1:])
