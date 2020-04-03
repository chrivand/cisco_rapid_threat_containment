#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtclogger

# import xml.etree.ElementTree as ET

def main(argv):
    debug_level = 0
    mylogger = rtclogger.LOGGER("get config",debug_level,"")

    try:
        if 'REQUEST_METHOD' in os.environ :
            order = str(sys.stdin.read())
            ppost = json.loads(order)
            table = ppost["table"]
        else:
            table = ""
            
        dbconn = rtcdb.RTCDB()
        dbresult  = dbconn.getXconfig(table)
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
