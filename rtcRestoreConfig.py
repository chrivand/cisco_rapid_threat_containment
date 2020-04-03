#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtclogger


def main(argv):

# todo - 
# input validation is for wimps
#
    print("Content-type:application/json\n\n")
    try:
        debug_level = 0        
        mylogger = rtclogger.LOGGER("Config ",debug_level,"")        
        order = str(sys.stdin.read())
        ppost = json.loads(order)
        config= ppost["config"]

        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.restoreConfig(config);
        if dbresult["rtcResult"] == "OK":
            rsp = {"rtcResult":"OK"}
        else:
            rsp = {"rtcResult":"DB ERROR","info": dbresult["info"]}
        print(json.dumps(rsp))

    except Exception as err:
        result = { "result":"Error","info":"some error {} config {}".format(mylogger.exception_info(err),config) }
        print(json.dumps(result))

if __name__ == "__main__":
    main(sys.argv[1:])
