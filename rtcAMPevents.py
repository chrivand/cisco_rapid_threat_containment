#!/usr/bin/python3                                                                                                                         
import json
import sys
import os
import cats
import rtcdb
import rtclogger

## define structure for simple gets (atomic structure)

def main(argv):

    debug_level = 0
    mylogger = rtclogger.LOGGER("AMPeventDetails",debug_level,"")
    
    try:
#        creds = json.loads(open("/tmp/config.json").read())
        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getAMPconfig()
        creds = json.loads(dbresult["configstring"])
        API_CLIENT_ID = creds["amp_api_client_id"]
        API_KEY = creds["amp_api_key"]
        a = cats.AMP(cloud="us",api_client_id=API_CLIENT_ID,api_key=API_KEY,debug=False,logfile="/tmp/rtcAMPevents.log")
        rsp = a.events(days=10)
        rsp.update({"rtcResult":"OK"})
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))
    


if __name__ == "__main__":
    main(sys.argv[1:])
