#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtcdb
from time import gmtime,strftime
from datetime import datetime,timedelta
import time

def exception_info(err):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
    return estring

def main(argv):

#
    try:
        mydb = rtcdb.RTCDB()
        print("Restting DB")
        mydb.reset_db(False)
        days = 1
        hours = 1
        fromdate = (datetime.utcnow() - timedelta(days=int(days),hours = int(hours))).strftime('%Y-%m-%d %H:%M:%S')

        MAC1 = "00:0C:29:80:DA:28"
        MAC2 = "00:0C:29:A9:79:69"
        MAC3 = "6C:96:CF:DC:F5:37"
        MAC4 = "00:50:56:C0:00:01"
        MAC5 = "08:6D:41:D3:E8:AA"

        print("Updating hosts")
        mydb.updateHost(MAC1,10)
        mydb.updateHost(MAC2,80)
        mydb.updateHost(MAC3,90)
        mydb.updateHost(MAC4,44)
        mydb.updateHost(MAC5,14)
        mydb.updateHost(MAC5,13)
        print("Getting hosts")        
        rsp = mydb.getHosts(MAC1)
        print(json.dumps(rsp,indent=4,sort_keys=True))
        rsp = mydb.getHosts()
        print(json.dumps(rsp,indent=4,sort_keys=True))

        ampevent = {
                    'AMP_hash' : AMP_hash,
                    'AMP_connector_guid' : "333333333",
                    'AMP_date' : "2018-10-01T21:330z",
                    'AMP_hostname' : "VMRAT13.labrats.se",
                    'AMP_MAC' : MAC1,
                    'AMP_IP' : "192.168.22.13"
                    }

        print("Insert AMP event")                
        mydb.insertAMPevent(MAC1,10,json.dumps(ampevent))
        print("GET AMP  events")        
        rsp = mydb.getAMPevents(MAC1)
        print(json.dumps(rsp,indent=4,sort_keys=True))        
        umbevent = {"umbeventtype":"CnC"}
        print("Insert UMB event")                
        mydb.insertUMBevent(MAC1,10,json.dumps(umbevent))
        print("GET UMB  events")        
        rsp = mydb.getUMBevents(MAC1)
        print(json.dumps(rsp,indent=4,sort_keys=True))        
        swevent = {"sweventtype":"hostf flow violation"}
        print("Insert SW event")                
        mydb.insertSWevent(MAC1,10,json.dumps(swevent))
        print("GET SW  events")        
        rsp = mydb.getSWevents(MAC1)
        print(json.dumps(rsp,indent=4,sort_keys=True))        
    except Exception as err:
        temp = exception_info(err)
        print(temp)


if __name__ == "__main__":
    main(sys.argv[1:])
