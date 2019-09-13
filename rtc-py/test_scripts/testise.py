#!/usr/bin/python3                                                                                                              
import json
import sys
import requests
import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from time import gmtime,strftime
import datetime
import os
import getopt
import re
import base64
import xml.etree.ElementTree as ET
import cats

def commit_suicide():
    print("Exception!" + str(err))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    sys.exit(2)

def print_help():
    print("running python " + str(sys.version_info))
    name = os.path.basename(__file__)
    print("Usage: " + name + " -s server -u username -p password -a( list active sessions) -P <policy> -I <ip address> -M <mac address>")
    print("not specifying the -p policy option deletes the ANC assignment")
    print("not specifying any option retrieves all endpoints with ANC assignment")

def main(argv):

    server = "10.1.41.70"
    username = "ERSadmin"
    password = "C!sco123"
    policy = ""
    ip     = ""
    mac    = ""
    list_active = False
    list_policies = False
    debug  = False
    try:
        opts, args = getopt.getopt(argv,"aldhs:u:p:P:I:M:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
        if opt == '-a':
            list_active = True
        if opt == '-l':
            list_policies = True
        if opt == '-d':
            debug = True
        if opt == ("-P"):
            policy = arg
        if opt == ("-I"):
            ip = arg
        if opt == ("-M"):
            mac = arg
        if opt == ("-s"):
            server = arg
        if opt == ("-u"):
            username = arg
        if opt == ("-p"):
            password = arg

    if debug:
        print("debug is on")
    ise_anc = cats.ISE_ANC(server,username,password,debug)
    
    
    if policy:
        ise_anc.applyPolicy(ip,mac,policy)
    else:
        if ip or mac:
            ise_anc.clearPolicy(ip,mac)
    MAC = ""

#    rsp = ise_anc.macPolicy(MAC)
#    print(json.dumps(rsp,indent=4,sort_keys=True))
    print("MAC POLICY FOR ALL")
    rsp = ise_anc.macPolicy("")
    print(json.dumps(rsp,indent=4,sort_keys=True))
    print("MAC POLICY FOR ONE")
    MAC = "00:0C:29:80:DA:28"    
    rsp = ise_anc.macPolicy(MAC)
    print(json.dumps(rsp,indent=4,sort_keys=True))
    
    rsp = ise_anc.endpoints()
    resources = rsp["SearchResult"]["resources"]
    for item in resources:
        r1 = ise_anc.endpoints(item["id"])
        print(json.dumps(rsp,indent=4,sort_keys=True))
        print("MAC:" + r1["ErsAncEndpoint"]["macAddress"] + "  POLICY:" + r1["ErsAncEndpoint"]["policyName"])

    if list_policies:
        print("listing policies")
        sessions = ise_anc.listPolicies()
        print(json.dumps(sessions,indent=4,sort_keys=True))
        
    if list_active:
        sessions = ise_anc.activeSessions()
        print(json.dumps(sessions,indent=4,sort_keys=True))
    
if __name__ == "__main__":
    main(sys.argv[1:])
