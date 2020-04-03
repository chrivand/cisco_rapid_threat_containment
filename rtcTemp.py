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
    mylogger = rtclogger.LOGGER("AMPeventDetails",debug_level,"")

    try:
        ip = "10.1.33.100"
#        creds = json.loads(open("/tmp/config.json").read())
        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getXconfig("swconfig")
        creds = json.loads(dbresult["configstring"])
        SW_SERVER = creds["sw_server"]
        SW_USERNAME = creds["sw_username"]
        SW_PASSWORD = creds["sw_password"]
#        print("connecting to ....{} {} {}".format(SW_SERVER,SW_USERNAME,SW_PASSWORD))

        sw = cats.SW(server=SW_SERVER,username=SW_USERNAME,password=SW_PASSWORD,debug=False)
        rsp = sw.flowsFromIP(ipaddress=ip,days=3,hours=0)
        rsp.update({"rtcResult":"OK"})
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp,indent=4,sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
