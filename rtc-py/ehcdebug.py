#!/usr/bin/python3
import cgi, os
import sys
import ehc
import ehcdb
import json


import cgitb; cgitb.enable()

try:


    esaconfig = ""
    start = False
    dbconn = ehcdb.EHCDB()
    dbresult  = dbconn.getEmailConfig()
    if dbresult["result"] == "OK":
        configstring  = dbresult["configstring"]
        econfig = json.loads(configstring)
        approved_nameservers = ["173.38.200.100"]
        approved_mx_hostnames =	["mx1.cisco.c3s2.iphmx.com","mx1.cisco.c3s2.iphmx.com"]
    else:
        raise Exception("Database Error")
    ehc = ehc.EHC(esaconfig)
    ehc.dmarc_check(econfig["domain_name"],approved_nameservers,approved_mx_hostnames)
    tests = ehc.get_result()
    rsp = {"result":"OK"}
    rsp.update({"checks":tests})
except Exception as err:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
    rsp = {"result":"Error:" + estring}    

print("Content-type:application/json\n\n")
print(json.dumps(rsp))



