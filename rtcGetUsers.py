#!/usr/bin/python3
import json
import sys
import os
import cats
import rtcdb
import cats
import rtclogger
from ldap3 import Server, Connection, ALL

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
        dbresult = dbconn.getXconfig("adconfig")
        ad_config = json.loads(dbresult["configstring"])
        try:
            ad_server = Server(ad_config["ad_server"],get_info = ALL)
            ad_conn   = Connection(ad_server,user=ad_config["ad_username"],password=ad_config["ad_password"], auto_bind = True)
        except Exception as err:
            estring = mylogger.exception_info(err)
            ad_conn = None

        dbresult = dbconn.getXconfig("ampconfig")
        creds = json.loads(dbresult["configstring"])
        
        rsp = dbconn.getUsers()
        users = rsp["items"]
        mylogger.log_debug(7,json.dumps(users))

        for u in users:
            mylogger.log_debug(7,"User is ".format(json.dumps(u)))

            ad_info = {
                "memberOf": [],
                "mail":     "",
                "badPasswordTime":"",
                "lastLogon":"",
                "badPwdCount":"",
                
                }
            try:
                if ad_conn:
                    ad_conn.search(u["user"],'(objectclass=person)',attributes=['sn','mail','memberOf','badPasswordTime','lastLogon','badPwdCount'])
                    entry = ad_conn.entries[0]
                    ad_info["memberOf"] = entry.memberOf.values
                    ad_info["badPasswordTime"] = str(entry.badPasswordTime)
                    ad_info["mail"] = str(entry.mail)
                    ad_info["lastLogon"] = str(entry.lastLogon)
                    ad_info["badPwdCount"] = str(entry.badPwdCount)                                        
            except Exception as e:
                pass
            u.update({"ad_info":ad_info})
            
            try:
                rsp = dbconn.getAMPevents(user=u["user"])
                u.update({"ampevents":rsp})
            except Exception as err:
                estring = mylogger.exception_info(err)
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
