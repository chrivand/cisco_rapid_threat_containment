#!/usr/bin/python3
import json
import sys
import os
import cats
import rtcdb
import cats
import rtclogger

## define structure for simple gets (atomic structure)

def main(argv):

    ### default never log,change this if needed 
    debug_level = 0
    mylogger = rtclogger.LOGGER("gethosts",debug_level,"")
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
        dbresult = dbconn.getAMPconfig()
        creds = json.loads(dbresult["configstring"])

        AMP_api_client_id = creds["amp_api_client_id"]
        AMP_api_key = creds["amp_api_key"]

        amp = cats.AMP(cloud="us",api_client_id=AMP_api_client_id,api_key=AMP_api_key,debug=debug,logfile="")
        
        rsp = dbconn.getUsers()
        users = rsp["users"]
        mylogger.log_debug(7,json.dumps(users))
        for u in users:
            mylogger.log_debug(7,"User is ".format(json.dumps(u)))


            try:
                rsp = dbconn.getAMPevents(user=u["user"])
                u.update({"ampevents":rsp})
            except Exception as err:
                estring = mylogger.exception_info(err)
                print(estring)
                u.update({"ampevents":{} })

            try:
                rsp = dbconn.getSWevents(user=u["user"])
                u.update({"swevents":rsp})
            except Exception as err:
                u.update({"swevents":{} })
                
            try:
                rsp = dbconn.getUMBevents(user=u["user"])
                u.update({"umbevents":rsp})
            except Exception as err:
                u.update({"umbevents":{} })

        rsp = {"rtcResult":"OK"}
        rsp.update({"items": users})
        rsp.update({"recurring":recurring})
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    if not debug:
        print(json.dumps(rsp))
    else:
        print(json.dumps(rsp,indent=4,sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
