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
        days = 1
        hours = 1
        fromdate = (datetime.utcnow() - timedelta(days=int(days),hours = int(hours))).strftime('%Y-%m-%d %H:%M:%S')
        MAC1 = "00:0C:29:80:DA:28"
        MAC2 = "00:0C:29:A9:79:69"

        rsp = mydb.getAMPevents(MAC1)
        print(json.dumps(rsp,indent=4,sort_keys=True))        

        print("GET UMB  events")        
        rsp = mydb.getUMBevents(MAC1)
        print(json.dumps(rsp,indent=4,sort_keys=True))        

        print("GET SW  events")        
        rsp = mydb.getSWevents(MAC1)
        print(json.dumps(rsp,indent=4,sort_keys=True))        
    except Exception as err:
        temp = exception_info(err)
        print(temp)


if __name__ == "__main__":
    main(sys.argv[1:])
