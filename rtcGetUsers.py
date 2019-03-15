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
            debug = False
        else :
            debug = True
        debug = False

        post = str(sys.stdin.read())
        temp = json.loads(post)
        recurring = temp["recurring"]
        
        dbconn = rtcdb.RTCDB()
        rsp = dbconn.getUsers()
        users = rsp["users"]
        mylogger.log_debug(7,json.dumps(users))


        for u in users:
            mylogger.log_debug(7,"User is ".format(json.dumps(u)))


            try:
                rsp = dbconn.getAMPevents(user=u["user"])
                u.update({"ampevents":rsp})
            except Exception as err:
                estring = exception_info(err)
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
        rsp.update({"users": users})
        rsp.update({"recurring":recurring})
    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}
    print("Content-type:application/json\n\n")
    print(json.dumps(rsp))
    


if __name__ == "__main__":
    main(sys.argv[1:])
