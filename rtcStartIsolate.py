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
    debug = False
    mylogger = rtclogger.LOGGER("rtcQ",debug_level,"")
    
    try:
        post = str(sys.stdin.read())
        info = json.loads(post)
        guid = info["guid"]
#        creds = json.loads(open("/tmp/config.json").read())
        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getXconfig("ampconfig")
        creds = json.loads(dbresult["configstring"])
        
        AMP_api_client_id = creds["amp_api_client_id"]
        AMP_api_key = creds["amp_api_key"]
        amp = cats.AMP(cloud="us",api_client_id=AMP_api_client_id,api_key=AMP_api_key,debug=debug,logfile="")

        rsp = amp.startHostIsolation(guid=guid)
        
        rsp.update({"rtcResult":"OK"})
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))


if __name__ == "__main__":
    main(sys.argv[1:])
