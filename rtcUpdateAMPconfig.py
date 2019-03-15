#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtclogger


def main(argv):

    debug_level = 0
    mylogger = rtclogger.LOGGER("updateAMPconfig",debug_level,"")
    post = str(sys.stdin.read())

    creds = json.loads(post)
# todo - 
# input validation is for wimps
#
    try:
        dbconn = rtcdb.RTCDB()
        dbconn.updateAMPconfig(post)
        dbresult  = dbconn.getAMPconfig()
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
