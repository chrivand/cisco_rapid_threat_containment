#!/usr/bin/python3
import json
import sys
import os
import cats
import getopt

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

def print_help():
    print("Usage testpxgrid -h -i ip -m mac")
    
def main(argv):

    mac = ""
    ip  = ""
    debug = False
    try:
        opts, args = getopt.getopt(argv,"hi:m:")
        for opt, arg in opts:
            if opt == '-h':
                print_help()
                sys.exit(2)
            if opt == ("-d"):
                debug = True
            if opt == ("-i"):
                ip = arg
            if opt == ("-m"):
                mac = arg

    except Exception as err:

        print_help()
        sys.exit(2)

    try:

        creds = json.loads(open("iseconfig.json").read())
        ISE_SERVER = creds["ise_server"]
        ISE_USERNAME = creds["ise_username"]
        ISE_PASSWORD = creds["ise_password"]
        PXGRID_CLIENT_CERT = creds["pxgrid_client_cert"]
        PXGRID_CLIENT_KEY = creds["pxgrid_client_key"]
        PXGRID_CLIENT_KEY_PASSWORD = creds["pxgrid_client_key_pw"]
        PXGRID_SERVER_CERT = creds["pxgrid_server_cert"]
        PXGRID_NODENAME = creds["pxgrid_nodename"]


        i = cats.ISE_PXGRID(server=ISE_SERVER,username=ISE_USERNAME,password=ISE_PASSWORD,debug=debug,logfile="",clientcert=PXGRID_CLIENT_CERT,clientkey=PXGRID_CLIENT_KEY,clientkeypassword=PXGRID_CLIENT_KEY_PASSWORD,servercert=PXGRID_SERVER_CERT,nodename=PXGRID_NODENAME)

        if ip:
            print("getting IP {}".format(ip))        
            rsp = i.getSessions(ip=ip)
            print(json.dumps(rsp,indent=4,sort_keys=True))

        if mac:
            print("getting MAC {}".format(mac))
            rsp = i.getSessions(mac=mac)
            print(json.dumps(rsp,indent=4,sort_keys=True))            
        if not ip and not mac:
            print("getting all sessions")
            rsp = i.getSessions()
            print(json.dumps(rsp,indent=4,sort_keys=True))                        
            
    except Exception as err:
        print(exception_info(err))

    


if __name__ == "__main__":
    main(sys.argv[1:])
