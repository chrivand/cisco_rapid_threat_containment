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
        credstring = dbconn.getISEconfig()
        creds = json.loads(credstring)
        ISE_SERVER = creds["ise_server"]
        ISE_USERNAME = creds["ise_username"]
        ISE_PASSWORD = creds["ise_password"]
#        print("connecting to ....{} {} {}".format(SW_SERVER,SW_USERNAME,SW_PASSWORD))

        ise = cats.ISE_ANC(server=ISE_SERVER,username=ISE_USERNAME,password=ISE_PASSWORD,debug=False)
        rsp = ise.clearPolicy(ip,"")
        rsp.update({"rtcResult":"OK"})
    except Exception as err:
        rsp = {"rtcResult": exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))


if __name__ == "__main__":
    main(sys.argv[1:])
