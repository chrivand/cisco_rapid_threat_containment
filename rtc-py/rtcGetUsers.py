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

        ### now get info on IPs
        rsp = dbconn.getIPs()
        ips = rsp["ips"]
        mylogger.log_debug(7,json.dumps(ips))
        for thisip in ips:
            mylogger.log_debug(7,"IP is ".format(json.dumps(thisip)))

            try:
                rsp = dbconn.getAMPevents(ip=thisip["ip"])
                thisip.update({"ampevents":rsp})
            except Exception as err:
                estring = mylogger.exception_info(err)
                print(estring)
                thisip.update({"ampevents":{} })

            try:
                rsp = dbconn.getSWevents(ip=thisip["ip"])
                thisip.update({"swevents":rsp})
            except Exception as err:
                thisip.update({"swevents":{} })
                
            try:
                rsp = dbconn.getUMBevents(ip=thisip["ip"])
                thisip.update({"umbevents":rsp})
            except Exception as err:
                thisip.update({"umbevents":{} }) 

        ### now get info on Hostnames
        rsp = dbconn.getHostnames()
        hostnames = rsp["hostnames"]
        mylogger.log_debug(7,json.dumps(hostnames))
        for thishostname in hostnames:
            mylogger.log_debug(7,"Hostname is ".format(json.dumps(thishostname)))

            try:
                rsp = dbconn.getAMPevents(hostname=thishostname["hostname"])
                thishostname.update({"ampevents":rsp})
            except Exception as err:
                estring = mylogger.exception_info(err)
                print(estring)
                thishostname.update({"ampevents":{} })

            try:
                rsp = dbconn.getUMBevents(hostname=thishostname["hostname"])
                thishostname.update({"umbevents":rsp})
            except Exception as err:
                thishostname.update({"umbevents":{} }) 


            if True:
#####            if not recurring:
### cannot ask AMP API regularly from GUI, because causes rate limiting, will only work for small demo or rate limiting hits                
                try:
                    rsp = amp.computers(hostname=thishostname["hostname"])
                    thishostname.update({"guid":rsp["data"][0]["connector_guid"]})
                    thishostname.update({"isolation":rsp["data"][0]["isolation"]["status"]})
                    thishostname.update({"isolationavailable":rsp["data"][0]["isolation"]["available"]})                                
                except Exception as err:
                    thishostname.update({"guid":{} })
                    thishostname.update({"isolation":{} })
                    thishostname.update({"isolationavailable":{} })
            else:
                thishostname.update({"guid":{} })
                thishostname.update({"isolation":{} })
                thishostname.update({"isolationavailable":{} })
                
                
            
        rsp = {"rtcResult":"OK"}
        rsp.update({"users": users})
        rsp.update({"ips": ips})
        rsp.update({"hostnames": hostnames})        
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
