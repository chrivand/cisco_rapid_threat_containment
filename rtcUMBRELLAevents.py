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
            debug = True
            days = 0
            hours = 1
            minutes = 0

        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getXconfig("umbrellaconfig")
        creds = json.loads(dbresult["configstring"])

        API_ORGID = creds["u_orgid"]
        API_INVESTIGATE_TOKEN = creds["u_investigate_token"]
        API_ENFORCE_TOKEN = creds["u_investigate_token"]        
        API_SECRET = creds["u_secret"]
        API_KEY = creds["u_key"]
        
        u = cats.UMBRELLA(investigate_token=API_INVESTIGATE_TOKEN,enforce_token=API_ENFORCE_TOKEN,key=API_KEY,secret=API_SECRET,orgid=API_ORGID,debug=debug,logfile="")

        umb_rsp = u.reportSecurityActivity(days=days,hours=hours,minutes=minutes)
        rsp = {"rtcResult":"OK"}
        rsp.update({"events": umb_rsp["requests"]})

        print("Content-type:application/json\n\n")
        print(json.dumps(rsp))

    except Exception as err:    
        print("Content-type:application/json\n\n")
        rsp = {"rtcResult": mylogger.exception_info(err)}
        print(json.dumps(rsp))

if __name__ == "__main__":
    main(sys.argv[1:])
