#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtclogger
import cats


def main(argv):

# todo - 
# input validation is for wimps
#
    print("Content-type:application/json\n\n")
    try:
        debug_level = 0        
        mylogger = rtclogger.LOGGER("Config ",debug_level,"")        
        order = str(sys.stdin.read())
        ppost = json.loads(order)
        table= ppost["table"]
        post= ppost["post"]
        debugmsg = ""
        dbconn = rtcdb.RTCDB()
        
        if table == "iseconfig":

            if post["pxgrid_client_cert"]:
                post.update({"pxgrid_password":""})
            else:
                debugmsg = "not post client cert and iseconfig"
                ''' password based auth for ise may need to retrieve password if not already stored'''
                dbresult = dbconn.getXconfig("iseconfig")
                
                if dbresult["rtcResult"] == "OK":
                    configstring  = dbresult["configstring"]
                    iseconfig = json.loads(configstring)
                    if not "pxgrid_password" in iseconfig:
                        debugmsg = debugmsg + " not pxgrid password"
                        i = cats.ISE_PXGRID(server=post["ise_server"],nodename=post["pxgrid_nodename"],description="",debug=True,logfile="/tmp/rtc.log")
                        password = i.getPassword()
                        debugmsg = debugmsg + "password is " + password
                        i.activate()
                        post.update({"pxgrid_password":password})
                else:
                    rsp = {"rtcResult":"DB ERROR","info": debugmsg + dbresult["info"]}
                    print(json.dumps(rsp))
                    return
                      
        dbresult = dbconn.updateXconfig(table,json.dumps(post))
        if dbresult["rtcResult"] == "OK":
            dbresult  = dbconn.getXconfig(table)
            if dbresult["rtcResult"] == "OK":
                configstring  = dbresult["configstring"]
                rsp = {"rtcResult":"OK"}
                rsp.update({"configstring": configstring})
            else:
                rsp = {"rtcResult":"DB ERROR"+debugmsg}
        else:
            rsp = {"rtcResult":"DB ERROR","info": debugmsg + dbresult["info"]}
        print(json.dumps(rsp))

    except Exception as err:
        result = { "result":"Error","info":"some error {} table {} post {} {}".format(mylogger.exception_info(err),table,post,debugmsg) }
        print(json.dumps(result))

if __name__ == "__main__":
    main(sys.argv[1:])
