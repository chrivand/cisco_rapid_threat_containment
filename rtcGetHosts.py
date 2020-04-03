#!/usr/bin/python3
import json
import cats
import rtcdb
import cats
import rtclogger
import sys
import os

## define structure for simple gets (atomic structure)

def main(argv):

    ### default never log,change this if needed
    debug_level = 0
    mylogger = rtclogger.LOGGER("getHosts",debug_level,"")
    try:

        if 'REQUEST_METHOD' in os.environ :
        ### this is called as CGI script and we should avoid printouts
            debug = False
            post = str(sys.stdin.read())
            temp = json.loads(post)
            recurring = temp["recurring"]
        else :
        ### this is called via CLI for troubleshooting
            recurring = "True"
            debug = True
 
        dbconn = rtcdb.RTCDB()
        rsp = dbconn.getHosts()
        hosts = rsp["hosts"]
        mylogger.log_debug(7,json.dumps(hosts))

        i= None
        anc = None
        dbresult = dbconn.getXconfig("iseconfig")
        creds = json.loads(dbresult["configstring"])
        if "ise_server" in creds:
            ISE_SERVER = creds["ise_server"]
            ISE_USERNAME = creds["ise_username"]
            PXGRID_PASSWORD = creds["pxgrid_password"]
            PXGRID_CLIENT_CERT = creds["pxgrid_client_cert"]
            PXGRID_CLIENT_KEY = creds["pxgrid_client_key"]
            PXGRID_CLIENT_KEY_PASSWORD = creds["pxgrid_client_key_pw"]
            PXGRID_SERVER_CERT = creds["pxgrid_server_cert"]
            PXGRID_NODENAME = creds["pxgrid_nodename"]
            i = cats.ISE_PXGRID(server=ISE_SERVER,debug=debug,logfile="",clientcert=PXGRID_CLIENT_CERT,clientkey=PXGRID_CLIENT_KEY,clientkeypassword=PXGRID_CLIENT_KEY_PASSWORD,servercert=PXGRID_SERVER_CERT,nodename=PXGRID_NODENAME,password=PXGRID_PASSWORD)
            anc = cats.ISE_ANC(ISE_SERVER,ISE_USERNAME,ISE_PASSWORD,debug=debug,logfile="")

        a = None
        dbresult = dbconn.getXconfig("ampconfig")
        creds = json.loads(dbresult["configstring"])
        if "amp_api_client_id" in creds:
            API_CLIENT_ID = creds["amp_api_client_id"]
            API_KEY = creds["amp_api_key"]
            a = cats.AMP(cloud="us",api_client_id=API_CLIENT_ID,api_key=API_KEY,debug=debug,logfile="")

            
        for h in hosts:
            mylogger.log_debug(7,"Host is ".format(json.dumps(h)))


            if i:
                try:
                    mylogger.log_debug(7,"getting sessions for " + h["mac"])
                    rsp = i.getSessions(mac=h["mac"])
                    mylogger.log_debug(7,"pxgrid rsp  {}".format(json.dumps(rsp)))
                    h.update({"ise":rsp})
                except Exception as err:
                    mylogger.log_debug(2,"ise sessions " +  mylogger.exception_info(err))
                    h.update({"ise":{}})        
            else:
                h.update({"ise":{}})
                
            if a:    
                try:
                    ip = rsp["ipAddresses"][0]
                    rsp = a.computers(internal_ip = ip)
                    mylogger.log_debug(7,"AMP resp"+ json.dumps(rsp))
                    h.update({"amp":rsp})
                except Exception as err:
                    mylogger.log_debug(1,"amp exception" + mylogger.exception_info(err))
                    h.update({"amp":{}})
            else:
                h.update({"amp":{}})
                
            if anc:
                try:
                    mylogger.log_debug(7,"reading ISE ANC for " + h["mac"])                                
                    rsp = anc.macPolicy(h["mac"])
                    h.update({"ancpolicy":rsp["policy"]})
                except Exception as err:
                    h.update({"ancpolicy":""})
                    mylogger.log_debug(1,"ise anc  exception" + mylogger.exception_info(err))
            else:
                h.update({"ancpolicy":""})
                
# get all the rtcEvent for this host

            try:
                rsp = dbconn.getAMPevents(h["mac"])
                h.update({"ampevents":rsp})
            except Exception as err:
                h.update({"ampevents":{} })
                mylogger.log_debug(1,"ampevents exception" + mylogger.exception_info(err))
            try:
                rsp = dbconn.getSWevents(h["mac"])
                h.update({"swevents":rsp})
            except Exception as err:
                h.update({"swevents":{} })
                
            try:
                rsp = dbconn.getUMBevents(h["mac"])
                h.update({"umbevents":rsp})
            except Exception as err:
                h.update({"umbevents":{} })
                mylogger.log_debug(1,"umbevents  exception" + mylogger.exception_info(err))
                
        rsp = {"rtcResult":"OK"}
        rsp.update({"hosts": hosts})
        rsp.update({"recurring": recurring})
        
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))
    


if __name__ == "__main__":
    main(sys.argv[1:])
