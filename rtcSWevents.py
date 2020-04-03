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
    mylogger = rtclogger.LOGGER("SWevents",debug_level,"")

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
        dbresult = dbconn.getXconfig("swconfig")
        creds = json.loads(dbresult["configstring"])
        SW_SERVER = creds["sw_server"]
        SW_USERNAME = creds["sw_username"]
        SW_PASSWORD = creds["sw_password"]
#        print("connecting to ....{} {} {}".format(SW_SERVER,SW_USERNAME,SW_PASSWORD))

        sw = cats.SW(server=SW_SERVER,username=SW_USERNAME,password=SW_PASSWORD,debug=False)
        sw_rsp = sw.searchSecurityEvents(days=days,hours=hours,minutes=minutes,sourceip="",targetip="",wait=5)
        rsp = {"rtcResult":"OK"}
        rsp.update({"events": sw_rsp["data"]["results"]})

    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))


if __name__ == "__main__":
    main(sys.argv[1:])
