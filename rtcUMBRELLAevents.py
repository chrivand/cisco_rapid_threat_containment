#!/usr/bin/python3                                                                                                                         
import json
import sys
import os
import cats
import rtcdb
import rtclogger


def main(argv):

    debug_level = 0
    mylogger = rtclogger.LOGGER("AMPeventDetails",debug_level,"")
    try:

        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getUMBRELLAconfig()
        creds = json.loads(dbresult["configstring"])

        API_ORGID = creds["u_orgid"]
        API_INVESTIGATE_TOKEN = creds["u_investigate_token"]
        API_ENFORCE_TOKEN = creds["u_investigate_token"]        
        API_SECRET = creds["u_secret"]
        API_KEY = creds["u_key"]
        
        u = cats.UMBRELLA(investigate_token=API_INVESTIGATE_TOKEN,enforce_token=API_ENFORCE_TOKEN,key=API_KEY,secret=API_SECRET,orgid=API_ORGID,debug=False,logfile="/tmp/rtcUMBRELLAevents.py")

        rsp = u.reportSecurityActivity(days=1)
        rsp.update({"rtcResult":"OK"})
        print("Content-type:application/json\n\n")
        print(json.dumps(rsp))

    except Exception as err:    
        print("Content-type:application/json\n\n")
        rsp = {"rtcResult": mylogger.exception_info(err)}
        print(json.dumps(rsp))

if __name__ == "__main__":
    main(sys.argv[1:])
