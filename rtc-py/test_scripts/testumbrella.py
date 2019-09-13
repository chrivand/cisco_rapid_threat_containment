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
import cats

##### secrets and orgids used for the different APIs
API_ORGID = "insertyourown"
API_ENFORCE_TOKEN = "insertyourown"
API_INVESTIGATE_TOKEN = "insertyourown"
API_KEY = "insertyourown"
API_SECRET = "insertyourown"

def print_help():
    print("running python " + str(sys.version_info))
    name = os.path.basename(__file__)
    print("Usage: " + name + " -o { get | post | delete | investigate | report } -n dnsname-i ip  -u url -d (for debug) -D days -H hours -M minutes")
    print("print -o post -n dnsname -u url  ## add dnsname to enforce")
    print("print -o delete -n dnsname -u url  ## delete dnsname to enforce")
    print("print -o get -n dnsname -u url  ## list dnsnames to enforce")
    print("print -o investigate -n dnsname -i ip  ## investigate dns name or ip")
    print("print -o report -n dnsname -i ip  -D days -H hours -M minutes ## report dns name")    
    
def main(argv):

    domain = ""
    ip = ""
    url = ""
    operation = "get"
    debug = False
    days = 0
    hours = 1
    minutes = 0
    try:
        opts, args = getopt.getopt(argv,"dho:n:u:i:D:H:M:")
        for opt, arg in opts:
            if opt == '-h':
                print_help()
                sys.exit(2)
            if opt == ("-d"):
                debug = True
            if opt == ("-o"):
                operation = arg
            if opt == ("-n"):
                domain = arg
            if opt == ("-u"):
                url = arg
            if opt == ("-i"):
                ip = arg
            if opt == ("-D"):
                days = int(arg)
            if opt == ("-H"):
                hours = int(arg)
            if opt == ("-M"):
                minutes = int(arg)
                
    except Exception as err:
        
        print_help()
        sys.exit(2)

    try:
        creds = json.loads(open("umbrellaapi.json").read())
        API_ORGID = creds["orgid"]
        API_ENFORCE_TOKEN = creds["enforce_token"]
        API_INVESTIGATE_TOKEN = creds["investigate_token"]
        API_KEY = creds["key"]        
        API_SECRET = creds["secret"]        
    except Exception as e:
        print(str(e))
        print("Failed to open umbrellaapi.json")
        print("Ensure you have defined API_xxx stuff in the script for the script to work")
    if debug:
        print("Using API ORGID {}".format(API_ORGID))
        print("Using API ENFORCETOKEN {}".format(API_ENFORCE_TOKEN))
        print("Using API INVESTIGATETOKEN {}".format(API_INVESTIGATE_TOKEN))
        print("Using API KEY {}".format(API_KEY))        
        print("Using API SECRET {}".format(API_SECRET))        

    u = cats.UMBRELLA(investigate_token=API_INVESTIGATE_TOKEN,enforce_token=API_ENFORCE_TOKEN,key=API_KEY,secret=API_SECRET,orgid=API_ORGID,debug=debug)
    
    if operation == "get":
        print("Listing domain on blacklist ")
        rsp = u.listEnforcement()
        print(json.dumps(rsp,indent=4,sort_keys=True))

    if operation == "post":
        print("Adding domain to blacklist {}".format(domain))
        rsp = u.addEnforcement(domain,url)
        print(json.dumps(rsp,indent=4,sort_keys=True))

    if operation == "delete":
        print("Deleting domain from blacklist {}".format(domain))
        rsp = u.deleteEnforcement(domain)
        print(json.dumps(rsp,indent=4,sort_keys=True))

    if operation == "report":
        print("Getting request on security activity! Days={} hours={} minutes={}".format(days,hours,minutes))
        rsp = u.reportSecurityActivity(days=days,hours=hours,minutes=minutes)
        print(json.dumps(rsp,indent=4,sort_keys=True))
        print("Getting destination activity for domain {}".format(domain))
        if domain:
            print("Getting identities for domain {}".format(domain))
            rsp = u.reportDestinationActivity(domain)
            print(json.dumps(rsp,indent=4,sort_keys=True))
            rsp = u.reportDestinationIdentities(domain)
            print(json.dumps(rsp,indent=4,sort_keys=True))

    if operation == "investigate":
        if domain:
            print("Investigate Domain Categories, domain: {}".format(domain))
            rsp = u.investigateCategories(domain)
            print(json.dumps(rsp,indent=4,sort_keys=True))
            print("Investigate DNSDB")            
            rsp = u.investigateDNSDB(domain)
            print("domains is " + domain)
            print(json.dumps(rsp,indent=4,sort_keys=True))
            print("Investigate Timeline")            
            rsp = u.investigateTimeline(domain)
            print("domains is " + domain)
            print(json.dumps(rsp,indent=4,sort_keys=True))
        if ip:
            print("Investigate IP for ip {}".format(ip))            
            rsp = u.investigateIP(ip)
            print(json.dumps(rsp,indent=4,sort_keys=True))

            print("Investigate IP Latest Domains")            
            rsp = u.investigateIPlatestDomains(ip)
            print(json.dumps(rsp,indent=4,sort_keys=True))
            
            print("Investigate IP Timelines")            
            rsp = u.investigateIPtimeline(ip)
            print(json.dumps(rsp,indent=4,sort_keys=True))


            

if __name__ == "__main__":
    main(sys.argv[1:])
