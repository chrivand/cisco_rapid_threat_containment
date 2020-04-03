#!/usr/bin/python3                                                                                                      
import json
import sys
import os
import cats
import rtcdb
import cats
import rtclogger

def main(argv):

    debug_level = 0
    mylogger = rtclogger.LOGGER("AMPeventDetails",debug_level,"")

    try:
        if 'REQUEST_METHOD' in os.environ :
            ### this is called as CGI script and we should avoid printouts
            debug = False
            post = str(sys.stdin.read())
            IPinfo = json.loads(post)
            ip = IPinfo["IP"]
        else :
        ### this is called via CLI for troubleshooting
            debug = True
            ip = "10.1.33.10"
            

        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getXconfig("swconfig")
        creds = json.loads(dbresult["configstring"])
        SW_SERVER = creds["sw_server"]
        SW_USERNAME = creds["sw_username"]
        SW_PASSWORD = creds["sw_password"]
        sw = cats.SW(server=SW_SERVER,username=SW_USERNAME,password=SW_PASSWORD,debug=False)
        rsp = sw.getFlows(sip=[ip],days=3,hours=0)
        rsp.update({"rtcResult":"OK"})
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    if debug:
        print(json.dumps(rsp,indent=4,sort_keys=True))
    else:
        print(json.dumps(rsp))


if __name__ == "__main__":
    main(sys.argv[1:])
