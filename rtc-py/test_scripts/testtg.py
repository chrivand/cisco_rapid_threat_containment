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
import cats

# change this key to yoru own API key, alternatively have the appropriate tgapikey.json file

API_KEY= "insertyourown"

try:
    creds = json.loads(open("tgapikey.json").read())
    API_KEY = creds["api_key"]
except Exception as e:
    print(str(e))
    print("Failed to open tgapikey.json")
    print("Ensure you have defined API_KEY in the script for the script to work")

print("using API_KEY {}".format(API_KEY))

searchstructure = [
        { "id": "domains", "search4what": "domain"},
        { "id": "ips", "search4what": "ip"},
        { "id": "urls", "search4what": "url"},
        { "id": "artifacts", "search4what": "artifact"},
        { "id": "paths", "search4what": "path"},
        { "id": "network_streams", "search4what": "network_stream"},
        { "id": "registry_keys", "search4what": "registry_key"},
]



def print_help():
    print("running python " + str(sys.version_info))
    name = os.path.basename(__file__)
    print("Usage: " + name + " -o <domains | ips .... etc > -s search -D number of days back -H number of hours back")
    print("..where -o is followed by what to search for, e.g.")
    print("./testtg -o domains -s www.cisco.com")
    print("./testtg -o ip -s 14.144.144.16")
    
    for s in searchstructure:
        print(s["id"])

def main(argv):

                   
    search = ""
    search4what = ""
    operation = "domains"
    days = 10
    hours = 1
    debug = False
    try:
        opts, args = getopt.getopt(argv,"dho:s:D:H:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit(2)
        if opt == '-d':
            debug= True

        if opt == ("-o"):
            operation = arg
            found = False
            for s in searchstructure:
                if operation == s["id"]:
                    found = True
                    search4what = s["search4what"]
                    break
            if not found:
                print("Invalid -o option")
                print_help()
                sys.exit(2)
        if opt == ("-s"):
            search = arg
        if opt == ("-D"):
            days = int(arg)
        if opt == ("-H"):
            print(arg)
            hours = int(arg)


    tg = cats.TG(API_KEY,debug=debug,logfile="")
    if operation == "domains":
        rsp = tg.searchDomain(domain=search,days=days,hours=hours)
    if operation == "ips":
        print("ip is " + search)
        rsp = tg.searchIP(ip=search,days=days,hours=hours)
    if operation == "urls":
        print("URL is " + search)
        rsp = tg.searchURL(url=search,days=days,hours=hours)
        


    print(json.dumps(rsp,indent=4,sort_keys=True))

        
if __name__ == "__main__":
    main(sys.argv[1:])
