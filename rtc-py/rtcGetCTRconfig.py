#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtclogger

# import xml.etree.ElementTree as ET

def main(argv):
    debug_level = 0
    mylogger = rtclogger.LOGGER("getAMPconfig",debug_level,"")

    try:
        dbconn = rtcdb.RTCDB()
        dbresult  = dbconn.getCTRconfig()
        if dbresult["rtcResult"] == "OK":
            configstring  = dbresult["configstring"]
            rsp = {"rtcResult":"OK"}
            rsp.update({"configstring": configstring})
        else:
            rsp = {"rtcResult":"DB ERROR"}
        
        ret = json.dumps(rsp)
        print("Content-type:application/json\n\n")        
        print (ret)

    except Exception as err:
        print("Content-type:application/json\n\n")
        result = { "result":"Error","info":"some error {}".format(mylogger.exception_info(err)) }
        print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])
