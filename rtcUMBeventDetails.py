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
    mylogger = rtclogger.LOGGER("SWeventDetails",debug_level,"")

    try:

        if 'REQUEST_METHOD' in os.environ :
            debug = False
        else :
            debug = True
        debug = False

        post = str(sys.stdin.read())
        temp = json.loads(post)
        eventid = temp["eventid"]
 
        dbconn = rtcdb.RTCDB()
        eventDetails = dbconn.getUMBeventById(eventid)

                
        rsp = {"rtcResult":"OK"}
        rsp.update({"eventDetails": eventDetails})
        
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))
    


if __name__ == "__main__":
    main(sys.argv[1:])
