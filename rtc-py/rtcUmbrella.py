#!/usr/bin/python3
import cats
import json
from datetime import datetime
import time
import sys
import os

def exception_info(err):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
    return estring

def main(argv):

## define credentials and API tokens
    ISE_SERVER = "10.1.41.70"
    ISE_USERNAME = "ERSadmin"
    ISE_PASSWORD = "C!sco123"
    ANC_POLICY = "QUARANTINE"    

    UMB_investigate_token = ""
    UMB_enforce_token = ""
    UMB_orgid = ""
    UMB_secret = ""
    UMB_key = ""
    
    UMB_investigate_token = ""
    UMB_enforce_token = ""
    UMB_orgid = "1865433"
    UMB_secret = "f90e76e1d25247798ede7291c54723fb"
    UMB_key = "df89d87980b94a07980e16942134580a"

    

    ise_anc = cats.ISE_ANC(ISE_SERVER,ISE_USERNAME,ISE_PASSWORD,debug=False)
    if not ise_anc:
        print("could not init ise ... IP not reachable or wrong username password")
        sys.exit(2)
    umb = cats.UMBRELLA(investigate_token=UMB_investigate_token,enforce_token=UMB_enforce_token,key=UMB_key,secret=UMB_secret,orgid=UMB_orgid,debug=False)
    if not umb:
        print("could not init Umbrella instance ... ")
    while True:
        try:
            UMB_rsp = umb.reportSecurityActivity(days=0,hours=0,minutes=1) 

            if UMB_rsp["catsresult"] == "OK":
                print("Umbrella response received")
                print(json.dumps(UMB_rsp,indent=4,sort_keys=True))
                UMB_activities = UMB_rsp["requests"]
                for activity in UMB_activities:
                    if "Command and Control" in activity["categories"]:
                        print("Found Command and Control activity")
                        thisMAC = ""
                        internalIP = activity["internalIp"]
                        print("applying ANC Policy {} to IP {}".format(ANC_POLICY,internalIP))
                        anc_rsp = ise_anc.applyPolicy(internalIP,thisMAC,ANC_POLICY)
                        if anc_rsp["catsresult"] == "OK":
                            print("policy applied")
                        else:
                            print("Error in cats result, maybe already applied ANC Policy for this IP? {}: {}".format(anc_rsp["catsresult"],anc_rsp["info"]))                        
            else:
                print("Error in cats result {}: {}".format(UMB_rsp["catsresult"],UMB_rsp["info"]))
        except Exception as err:
            print(exception_info(err))
        time.sleep(59)
        
if __name__ == "__main__":
    main(sys.argv[1:])
