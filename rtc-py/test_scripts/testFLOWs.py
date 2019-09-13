#!/usr/bin/python3                                                                                                      
import json
import sys
import os
import cats
import rtcdb
import cats

## define structure for simple gets (atomic structure)
def log_debug(logmessage):
    f = open("/tmp/rtclog","a")
    f.write(logmessage)
    f.close()

def error_log(err):
    log_debug("Exception! {}\n ".format(str(err)))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    log_debug("{} {} {}".format(exc_type, fname, exc_tb.tb_lineno))

def exception_info(err):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
    return estring

def main(argv):

    try:
        ip = "192.168.22.10"
#        creds = json.loads(open("/tmp/config.json").read())
        dbconn = rtcdb.RTCDB()
        credstring = dbconn.getCredentials()
        creds = json.loads(credstring)
        SW_SERVER = creds["sw_server"]
        SW_USERNAME = creds["sw_username"]
        SW_PASSWORD = creds["sw_password"]
#        print("connecting to ....{} {} {}".format(SW_SERVER,SW_USERNAME,SW_PASSWORD))

        sw = cats.SW(server=SW_SERVER,username=SW_USERNAME,password=SW_PASSWORD,debug=False)
        rsp = sw.flowsFromIP(ipaddress=ip,days=3,hours=0)
#        rsp.update({"rtcResult":"OK"})
    except Exception as err:
        rsp = {"rtcResult": exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))


if __name__ == "__main__":
    main(sys.argv[1:])
