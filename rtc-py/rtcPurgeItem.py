#!/usr/bin/python3
import json
import sys
import os
import cats
import rtcdb
import cats
import rtclogger

## define structure for simple gets (atomic structure)

def main(argv):

    ### default never log,change this if needed
    try:
        
        debug_level = 0
        mylogger = rtclogger.LOGGER("gethosts",debug_level,"")


        if 'REQUEST_METHOD' in os.environ :
            ### this is called as CGI script and we should avoid printouts                                                              
            debug = False
            post = str(sys.stdin.read())
            temp = json.loads(post)
            table = temp["type"]                        
            name = temp["name"]
        else :
            debug = True
            table = input("Enter table to purge:")            
            name = input("Enter name to purge:")
        if table == "mac" or table == "hostname" or table == "user" or table == "ip":
            dbconn = rtcdb.RTCDB()
            if table == "ip":
                rsp = dbconn.deleteIP(name)
            if table == "mac":
                rsp = dbconn.deleteHost(name)
            if table == "hostname":
                rsp = dbconn.deleteHostname(name)
            if table == "user":
                rsp = dbconn.deleteUser(name)
                
            rsp = {"rtcResult": "OK"}
        else:
            rsp = {"rtcResult": "Error - Invalid Table"}
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}

    print("Content-type:application/json\n\n")
    if not debug:
        print(json.dumps(rsp))
    else:
        print(json.dumps(rsp,indent=4,sort_keys=True))

if __name__ == "__main__":
    main(sys.argv[1:])
