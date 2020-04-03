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
        post = str(sys.stdin.read())
        IPinfo = json.loads(post)
        mac = IPinfo["MAC"]
#        creds = json.loads(open("/tmp/config.json").read())
        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getXconfig("iseconfig")
        creds = json.loads(dbresult["configstring"])
        ISE_SERVER = creds["ise_server"]
        ISE_USERNAME = creds["ise_username"]
        ISE_PASSWORD = creds["ise_password"]
#        print("connecting to ....{} {} {}".format(SW_SERVER,SW_USERNAME,SW_PASSWORD))

        ise = cats.ISE_ANC(server=ISE_SERVER,username=ISE_USERNAME,password=ISE_PASSWORD,debug=False)
        rsp = ise.clearPolicy(mac=mac)
        rsp.update({"rtcResult":"OK"})
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))


if __name__ == "__main__":
    main(sys.argv[1:])
