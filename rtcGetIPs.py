#!/usr/bin/python3
import json
import sys
import os
import cats
import rtcdb
import cats
import rtclogger
import time
## define structure for simple gets (atomic structure)

def main(argv):

    ### default never log,change this if needed 
    debug_level = 0
    mylogger = rtclogger.LOGGER("gethosts",debug_level,"")
    try:
        if 'REQUEST_METHOD' in os.environ :
            ### this is called as CGI script and we should avoid printouts                                                              
            debug = False
            post = str(sys.stdin.read())
            temp = json.loads(post)
            recurring = temp["recurring"]
        else :
        ### this is called via CLI for troubleshooting                                                                              
            recurring = "True"
            debug = True

        dbconn = rtcdb.RTCDB()
        
        ### now get info on IPs
        rsp = dbconn.getIPs()
        ips = rsp["items"]
        mylogger.log_debug(7,json.dumps(ips))
        for thisip in ips:
            mylogger.log_debug(7,"IP is ".format(json.dumps(thisip)))
            
            try:
                rsp = dbconn.getAMPevents(ip=thisip["ip"])
                thisip.update({"ampevents":rsp})
            except Exception as err:
                estring = mylogger.exception_info(err)
                thisip.update({"ampevents":{} })

            try:
                rsp = dbconn.getUMBevents(ip=thisip["ip"])
                thisip.update({"umbevents":rsp})
            except Exception as err:
                estring = mylogger.exception_info(err)
                thisip.update({"umbevents":{} }) 
                
            try:
                rsp = dbconn.getSWevents(ip=thisip["ip"])
                thisip.update({"swevents":rsp})
            except Exception as err:
                estring = mylogger.exception_info(err)
                thisip.update({"swevents":{} })
                

        rsp = {"rtcResult":"OK"}
        rsp.update({"items": ips})
        rsp.update({"recurring":recurring})
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    if not debug:
        print(json.dumps(rsp))
    else:
        print(json.dumps(rsp,indent=4,sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
