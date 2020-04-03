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
        if 'REQUEST_METHOD' in os.environ :
            ### this is called as CGI script and we should avoid printouts
            debug = False
            post = str(sys.stdin.read())
            request = json.loads(post)
            days = int(request["days"])
            hours = int(request["hours"])
            minutes = int(request["hours"])                        
        else :
        ### this is called via CLI for troubleshooting
            recurring = "True"
            debug = True
            days = 0
            hours = 1
            minutes = 0
            
        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getXconfig("ampconfig")
        creds = json.loads(dbresult["configstring"])
        API_CLIENT_ID = creds["amp_api_client_id"]
        API_KEY = creds["amp_api_key"]
        a = cats.AMP(cloud="us",api_client_id=API_CLIENT_ID,api_key=API_KEY,debug=False,logfile="/tmp/rtcAMPevents.log")
        amp_rsp = a.events(days=days,hours=hours,minutes=minutes)
        
        rsp = {"rtcResult":"OK"}
        rsp.update({"events": amp_rsp["data"]})


    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))
    


if __name__ == "__main__":
    main(sys.argv[1:])
