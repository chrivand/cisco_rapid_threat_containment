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

        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getXconfig("iseconfig")
        creds = json.loads(dbresult["configstring"])
        ISE_SERVER = creds["ise_server"]
        ISE_USERNAME = creds["ise_username"]
        PXGRID_CLIENT_CERT = creds["pxgrid_client_cert"]
        PXGRID_CLIENT_KEY = creds["pxgrid_client_key"]
        PXGRID_CLIENT_KEY_PASSWORD = creds["pxgrid_client_key_pw"]
        PXGRID_SERVER_CERT = creds["pxgrid_server_cert"]
        PXGRID_NODENAME = creds["pxgrid_nodename"]
        if "pxgrid_password" in creds:
            PXGRID_PASSWORD = creds["pxgrid_password"]
        else:
            PXGRID_PASSWORD = ""
        if 'REQUEST_METHOD' in os.environ :
            debug = False
        else :
            debug = True
#        print("connecting to ....{} {} {}".format(ISE_SERVER,ISE_USERNAME,ISE_PASSWORD))
        i = cats.ISE_PXGRID(server=ISE_SERVER,password=PXGRID_PASSWORD,debug=debug,logfile="",clientcert=PXGRID_CLIENT_CERT,clientkey=PXGRID_CLIENT_KEY,clientkeypassword=PXGRID_CLIENT_KEY_PASSWORD,servercert=PXGRID_SERVER_CERT,nodename=PXGRID_NODENAME)
#        i = cats.ISE_PXGRID(server=ISE_SERVER,username=ISE_USERNAME,password=ISE_PASSWORD,debug=True,logfile="")        
        rsp = i.getSessions()
#        print(str(rsp))
        rsp.update({"rtcResult":"OK"})
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))
    


if __name__ == "__main__":
    main(sys.argv[1:])
