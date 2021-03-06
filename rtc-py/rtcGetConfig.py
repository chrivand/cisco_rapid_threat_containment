#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import cats
import os
import rtclogger

def main(argv):

    debug_level = 0
    mylogger = rtclogger.LOGGER("AMPeventDetails",debug_level,"")
    try:
        dbconn = rtcdb.RTCDB()

        dbresult  = dbconn.getRTCconfig()
        if dbresult["rtcResult"] == "OK":
            configstring  = dbresult["configstring"]
            rsp = {"rtcResult":"OK"}
            rsp.update({"configstring": configstring})        
        else:
            rsp = {"rtcResult":"DB ERROR"}
            
        print("Content-type:application/json\n\n")
        print(json.dumps(rsp))


    except Exception as err:
        print("Content-type:application/json\n\n")
        result = { "rtcResult":"Error","info":"some error {}".format(mylogger.exception_info(err)) }
        print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])
