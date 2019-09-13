#!/usr/bin/python3                                                                                                                         
import json
import sys
import requests
import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from time import gmtime,strftime
from datetime import datetime,timedelta
import time
import os
import getopt
import re
import base64
# import xml.etree.ElementTree as ET
import xml.etree.ElementTree
import ipaddress
from requests.auth import HTTPBasicAuth
import cats
## define structure for simple gets (atomic structure)

API_GETS = [
        {"id": "tenants","apipath":"/tenants/","comment":"show tenant id (boring)","tag_required":False},
        {"id": "tenantid","apipath":"/tenants/{0}","comment":"show info for specific tenant id - very boring","tag_required":False},
        {"id": "eventlist","apipath":"/tenants/{0}/security-events/templates","comment":"show event list ","tag_required":False},
        {"id": "custhosts","apipath":"/tenants/{0}/customHosts/tags","comment":"Show tags for custom hosts","tag_required":False},
        {"id": "geos","apipath":"/tenants/{0}/externalGeos/tags","comment":"Show tags for external Geos","tag_required":False},
        {"id": "geosalarms","apipath":"/tenants/{0}/externalGeos/{1}/alarms/topHosts","comment":"Show alarms for external Geos with tag (specify with -t)","tag_required":True},
        {"id": "geostraffic","apipath":"/tenants/{0}/externalGeos/{1}/traffic/hourly","comment":"Show trafic for external Geos with tag (specify with -t)","tag_required":True},
        {"id": "geosraw","apipath":"/tenants/{0}/externalGeos/{1}/traffic/raw","comment":"Show raw traffic for external Geos with tag (specify with -t)","tag_required":True},
        {"id": "externalthreatstags","apipath":"/tenants/{0}/externalThreats/tags/","comment":"Show external threats tags","tag_required":False},
        {"id": "externalthreatsfortag","apipath":"/tenants/{0}/externalThreats/tags/{1}","comment":"Show external threat for tag - specify tag with -t <tag>","tag_required":True},
    {"id": "externalthreatsalarmstophosts","apipath":"/tenants/{0}/externalThreats/tags/{1}/alarms/topHosts","comment":"Show external threats top alarms for tophosts - specify tag with -t <tag>","tag_required":True},
    {"id": "externalthreats","apipath":"/tenants/{0}/externalThreats/tags/{1}/alarms/topHosts","comment":"Show external threats top alarms  - specify tag with -t <tag>","tag_required":True},
        {"id": "externalthreatstraffichourly","apipath":"/tenants/{0}/externalThreats/tags/{1}/traffic/hourly","comment":"Show external threats top alarms  - specify tag with -t <tag>","tag_required":True},
    {"id": "externalthreatstrafficraw","apipath":"/tenants/{0}/externalThreats/tags/{1}/traffic/raw","comment":"Show external threats top alarms  - specify tag with -t <tag>","tag_required":True},
    {"id": "flows", "apipath":"","comment":"Show flows for host","tag_required":False},

]

## define structure for complex operation, first a post to initate search, then subsequent queries to see if search done, then fetch result
API_SEARCHES = [
    {"id": "secevents","postpath":"/tenants/{0}/security-events/queries","querypath":"/tenants/{0}/security-events/queries/{1}","resultpath":"/tenants/{0}/security-events/results/{1}","comment":"show security events"},
    {"id": "topports","postpath":"/tenants/{0}/flow-reports/top-ports/queries","querypath":"/tenants/{0}/flow-reports/top-ports/queries/{1}","resultpath":"/tenants/{0}/flow-reports/top-ports/results/{1}","comment":"show Flow Reports Top Ports"},
    {"id": "topapplications","postpath":"/tenants/{0}/flow-reports/top-applications/queries","querypath":"/tenants/{0}/flow-reports/top-applications/queries/{1}","resultpath":"/tenants/{0}/flow-reports/top-applications/results/{1}","comment":"show Flow Reports Top Applications"},
    {"id": "topprotocols","postpath":"/tenants/{0}/flow-reports/top-protocols/queries","querypath":"/tenants/{0}/flow-reports/top-protocols/queries/{1}","resultpath":"/tenants/{0}/flow-reports/top-protocols/results/{1}","comment":"show Flow Reports Top Protocols"},
    {"id": "tophosts","postpath":"/tenants/{0}/flow-reports/top-hosts/queries","querypath":"/tenants/{0}/flow-reports/top-hosts/queries/{1}","resultpath":"/tenants/{0}/flow-reports/top-hosts/results/{1}","comment":"show Flow Reports Top Hosts"},
    {"id": "toppeers","postpath":"/tenants/{0}/flow-reports/top-peers/queries","querypath":"/tenants/{0}/flow-reports/top-peers/queries/{1}","resultpath":"/tenants/{0}/flow-reports/top-peers/results/{1}","comment":"show Flow Reports Top Peers"},
    {"id": "topconversations","postpath":"/tenants/{0}/flow-reports/top-conversations/queries","querypath":"/tenants/{0}/flow-reports/top-conversations/queries/{1}","resultpath":"/tenants/{0}/flow-reports/top-conversations/results/{1}","comment":"show Flow Reports Top Conversations"},
{"id": "topservices","postpath":"/tenants/{0}/flow-reports/top-services/queries","querypath":"/tenants/{0}/flow-reports/top-services/queries/{1}","resultpath":"/tenants/{0}/flow-reports/top-services/results/{1}","comment":"show Flow Reports Top Services"},    
]        
def commit_suicide(err):
    print("Exception! {}\n ".format(str(err)))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    sys.exit(2)


def print_help():
    print("running python " + str(sys.version_info))
    name = os.path.basename(__file__)
    print("Usage: " + name + " -s server -u username -p password -o operation -S <source ip> -T <target ip> -D days -H hours -M minutes-d ")
    print("-D Days and -H hours -M minutes back in time to search")
    print("-d adds debugging")
    for operation in API_GETS:
        print("-o " + operation["id"] + " # " + operation["comment"])
    for operation in API_SEARCHES:
        print("-o " + operation["id"] + " # " + operation["comment"])
    
    sys.exit()
def main(argv):

    server = "smc.labrats.se"
    username = "smc-api"
    password = "C!sco123"
    tag = ""
    debug = False
    sourceip = ""
    targetip   = ""
    days = 0
    hours = 1
    minutes = 1    
    wait = 3
    operation = "secevents"
    try:
        opts, args = getopt.getopt(argv,"hds:w:u:p:o:t:D:H:M:S:T:")
        for opt, arg in opts:
            if opt == '-h':
                print_help()
            if opt == ("-p"):
                password = arg
            if opt == ("-o"):
                operation = arg
            if opt == ("-t"):
                tag = str(arg)
            if opt == ("-D"):
                days = int(arg)
            if opt == ("-M"):
                minutes = int(arg)
            if opt == ("-w"):
                wait = int(arg)
            if opt == ("-H"):
                hours = int(arg)
            if opt == ("-d"):
                debug = True
            if opt == ("-S"):
                sourceip = arg
                try:
                    ipaddress.ip_address(sourceip)
                except:
                    print("-S sourceip is not a valid IP: {}".format(sourceip))
                    print_help()
                    sys.exit()
            if opt == ("-T"):
                targetip = arg
                try:
                    ipaddress.ip_address(targetip)
                except:
                    print("-T targetip is not a valid IP: {}".format(targetip))
                    print_help()
                    sys.exit()

    except getopt.GetoptError:
        print_help()
        sys.exit(2)


    print("Trying operation {} with tag={} and options days={} hours={} sourceip={} targetip={}".format(operation,tag,days,hours,sourceip,targetip))




    found = False
    for api_get in API_GETS:
        if operation == api_get["id"]:
            found =True
            apipath = api_get["apipath"]
            if api_get["tag_required"] and tag == "":
                print("operation {} requires a tag, specified with -t option!".format(operation))
                sys.exit()

    if found:
        sw = cats.SW(server,username,password,debug=debug,logfile="")
        if not apipath:
            rsp = sw.flowsFromIP(sourceip,days,hours,minutes)
            print(json.dumps(rsp,indent=4,sort_keys=True))
        else:
            print("getSWpath path=" + apipath)
            rsp = sw.getSWpath(path=apipath,tag=tag)
            if rsp:
                print(json.dumps(rsp,indent=4,sort_keys=True))
            else:
                print("Could not get stuff")
    else:
        for api_search in API_SEARCHES:
            if operation == api_search["id"]:
                found = True
                sw = cats.SW(server,username,password,debug=debug,logfile="")
                if operation == "secevents":
                    rsp = sw.searchSecurityEvents(days=days,hours=hours,minutes=minutes,sourceip=sourceip,targetip=targetip,wait=wait)
                else:
                    rsp = sw.searchFlowReports(operation=operation,days=days,hours=hours,minutes=minutes,sourceip=sourceip,targetip=targetip,wait=wait)
                if rsp:
                    print(json.dumps(rsp,indent=4,sort_keys=True))    
                else:
                    print("Some error occoured")
    if not found:
        print("invalid operation: -o with invalid option")
        print_help()
        sys.exit()



if __name__ == "__main__":
    main(sys.argv[1:])
