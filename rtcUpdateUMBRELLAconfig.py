#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtclogger

def main(argv):

    debug_level = 0
    mylogger = rtclogger.LOGGER("ISEconfig",debug_level,"")

    post = str(sys.stdin.read())
#    post = urllib.unquote(t).decode('utf8')
    creds = json.loads(post)
# todo - 
# input validation is for wimps
#
    try:
        dbconn = rtcdb.RTCDB()
        dbconn.updateUMBRELLAconfig(post)
        dbresult  = dbconn.getUMBRELLAconfig()
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
        result = { "result":"Error","info":"some error {}".format(mylogger.exception_info(err)) }
        print(json.dumps(result))
        return


if __name__ == "__main__":
    main(sys.argv[1:])
