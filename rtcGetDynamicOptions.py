#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import cats
import os
import rtclogger
from ldap3 import Server, Connection, ALL

def main(argv):
    debug_level = 0
    mylogger = rtclogger.LOGGER("GetDynOptions",debug_level,"")

    try:
        if 'REQUEST_METHOD' in os.environ :
            ### this is called as CGI script and we should avoid printouts                                                              
            debug = False
            post = str(sys.stdin.read())
            temp = json.loads(post)
            item = temp["item"]
        else :
            ### this is called via CLI for troubleshooting                                                                                item = "all"
            recurring = "True"
            debug = True
            item = "all"
            
        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getXconfig("adconfig")
        ADgroups = []                
        if item == "all" or item=="adconfig":
            ad_config = json.loads(dbresult["configstring"])
            if "ad_server" in ad_config:
                ad_server = Server(ad_config["ad_server"],get_info = ALL)
                ad_conn   = Connection(ad_server,user=ad_config["ad_username"],password=ad_config["ad_password"], auto_bind\
 = True)
                ad_conn.search(search_base=ad_config["ad_base_dn"],search_filter = '(objectclass=Group)',attributes=['cn'])
                groups = ad_conn.entries
                for group in groups:
                    ADgroups.append(group.cn.values[0])
        isePolicies = []                    
        if item == "all" or item=="iseconfig":                            
            dbresult = dbconn.getXconfig("iseconfig")
            iseconfig = json.loads(dbresult["configstring"])
            if "ise_server" in iseconfig:        
                server = iseconfig["ise_server"]
                username = iseconfig["ise_username"]
                password = iseconfig["ise_password"]                
                ise = cats.ISE_ANC(server=server,username=username,password=password,debug=False)
                isePolicies = ise.listPolicies()

        swEvents = []
        swHostGroups = []
        if item == "all" or item=="swconfig":                                    
            dbresult = dbconn.getXconfig("swconfig")
            swconfig = json.loads(dbresult["configstring"])
            if "sw_server" in swconfig:
                server = swconfig["sw_server"]
                username = swconfig["sw_username"]
                password = swconfig["sw_password"]                
                sw = cats.SW(server=server,username=username,password=password,debug=False)
                swEvents = sw.eventList()
                swHostGroups = sw.getHostGroups()
        ampEvents = []
        if item == "all" or item=="ampconfig":                                            
            dbresult = dbconn.getXconfig("ampconfig")
            ampConfig = json.loads(dbresult["configstring"])
            if "amp_api_client_id" in ampConfig:
                API_CLIENT_ID = ampConfig["amp_api_client_id"]
                API_KEY = ampConfig["amp_api_key"]
                amp = cats.AMP(cloud="us",api_client_id=API_CLIENT_ID,api_key=API_KEY,debug=False,logfile="")
                ampEvents = amp.eventTypes()
        

        rsp = {"rtcResult":"OK"}
        rsp.update({"item": item})                
        rsp.update({"ADgroups": ADgroups})                                   
        rsp.update({"swEvents": swEvents})
        rsp.update({"swHostGroups": swHostGroups})
        rsp.update({"ampEvents": ampEvents})
        rsp.update({"isePolicies": isePolicies})

        
        print("Content-type:application/json\n\n")

        ret = json.dumps(rsp)
        print (ret)

    except Exception as err:
        print("Content-type:application/json\n\n")
        result = { "rtcResult":"Error","info":"some error {}".format(mylogger.exception_info(err)) }
        print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])
