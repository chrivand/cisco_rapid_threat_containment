#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb

# import xml.etree.ElementTree as ET

def main(argv):

    try:
        dbconn = rtcdb.RTCDB()
        dbresult  = dbconn.getSWconfig()
        if dbresult["rtcResult"] == "OK":
            configstring  = dbresult["configstring"]
            rsp = {"rtcResult":"OK"}
            rsp.update({"configstring": configstring})
        else:
            rsp = {"rtcResult":"DB ERROR"}
        
        print("Content-type:application/json\n\n")
        ret = json.dumps(rsp)
        print (ret)

    except Exception as err:
        print("Content-type:application/json\n\n")
        result = { "result":"Error","info":"some error {}".format(err) }
        print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])
