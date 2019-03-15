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

        dbresult = dbconn.getSWconfig()
        swconfig = json.loads(dbresult["configstring"])
        server = swconfig["sw_server"]
        username = swconfig["sw_username"]
        password = swconfig["sw_password"]                
        sw = cats.SW(server=server,username=username,password=password,debug=False)
        swEvents = sw.eventList()

        dbresult = dbconn.getAMPconfig()
        ampConfig = json.loads(dbresult["configstring"])
        API_CLIENT_ID = ampConfig["amp_api_client_id"]
        API_KEY = ampConfig["amp_api_key"]

        amp = cats.AMP(cloud="us",api_client_id=API_CLIENT_ID,api_key=API_KEY,debug=False,logfile="")
        ampEvents = amp.eventTypes()
        

        rsp = {"rtcResult":"OK"}
        rsp.update({"swEvents": swEvents})
        rsp.update({"ampEvents": ampEvents})                   
        print("Content-type:application/json\n\n")

        ret = json.dumps(rsp)
        print (ret)

    except Exception as err:
        print("Content-type:application/json\n\n")
        result = { "rtcResult":"Error","info":"some error {}".format(mylogger.exception_info(err)) }
        print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])
