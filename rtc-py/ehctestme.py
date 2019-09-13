#!/usr/bin/python3
import cgi, os
import sys
import ehc
import ehcdb
import json


import cgitb; cgitb.enable()

try:
    post = str(sys.stdin.read())

    esaconfig = ""
    start = False
    for line in post.splitlines():
        if "<?xml" in line:
            start = True
        if start:
            esaconfig = esaconfig + line + '\n'
        if "</config>" in line:
            start = False
    dbconn = ehcdb.EHCDB()
    dbresult  = dbconn.getEmailConfig()
    if dbresult["result"] == "OK":
        configstring  = dbresult["configstring"]
        econfig = json.loads(configstring)
#        approved_nameservers = ["173.38.200.100"]
#        approved_mx_hostnames = ["mx1.cisco.c3s2.iphmx.com","mx2.cisco.c3s2.iphmx.com"]
        approved_nameservers = str.split(econfig["approved_nameservers"],",")
        approved_mx_hostnames = str.split(econfig["approved_mx_hostnames"],",")
    else:
        raise Exception("Database Error")
    
    ehc = ehc.EHC(esaconfig)
    ehc.get_licenses()
    ehc.check_rules()
    ehc.check_hat()
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



