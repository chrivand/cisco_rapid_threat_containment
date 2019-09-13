#!/usr/bin/python3


import json
import sys
import pprint
import time
import os
import getopt
import re
import cats



API_CLIENT_ID = "insertyourown"
API_KEY= "insertyourown"



operations = [
    "events",
    "eventtypes",
    "computers",
    "computerguid",
    "computertrajectory",
    "computeruseractivity",
    "computerusertrajectory",
    "eventstreams",
    "checkisolation",
    "isolate",
    "unisolate"
    ]
def print_help():
    print("running python " + str(sys.version_info))
    name = os.path.basename(__file__)
    print("Usage: " + name + " -h -o operation -D days -H hours - M minutes -d debug -n Hostname -g guid -i internal_ip -e external_\
ip ")
    print(".. where operation is ")
    print(".. -o events")
    print(".. -o eventtypes")
    print(".. -o computers <-i internal_ip -e external_ip -n hostname>")
    print(".. -o computerguid -g GUID")    
    print(".. -o computertrajectory -g guid -s <search for ip sha etc>")
    print(".. -o computerusertrajectory -g guid -s <search for ip sha etc>")
    print(".. -o computeruseractivity -g guid -s <search for ip sha etc>")
    print(".. -o eventstreams")
    print(".. -o checkisolation -g guid")
    print(".. -o startisolation -g guid")
    print(".. -o stopisolation -g guid")
    
def main(argv):

    debug = False
    days = 1
    hours = 1
    minutes = 1    
    internal_ip = ""
    external_ip = ""
    hostname    = ""
    operation = ""
    search = ""
    guid = ""
    
    try:
        opts, args = getopt.getopt(argv,"hdD:g:o:H:n:i:e:s:M:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit(2)
        if opt == ("-o"):
            operation = arg
            found = False
            for op in operations:
                if operation == op:
                    found = True
                    break
            if not found:
                print("Invalid -o option")
                print_help()
                sys.exit(2)
        if opt == ("-g"):
            guid = arg
        if opt == '-d':
            debug = True
        if opt == ("-D"):
            days = int(arg)
        if opt == ("-H"):
            hours = int(arg)
        if opt == ("-M"):
            minutes = int(arg)
        if opt == ("-i"):
            internal_ip = arg
        if opt == ("-e"):
            external_ip = arg
        if opt == ("-n"):
            hostname = arg
        if opt == ("-s"):
            search = arg

    if not operation:
        print("-o not specified")
        print_help()
        sys.exit(2)
    try:
        creds = json.loads(open("ampapi.json").read())
        API_CLIENT_ID = creds["api_client_id"]    
        API_KEY = creds["api_key"]

    except Exception as e:
        print(str(e))
        print("Failed to open ampapi.json")
        print("Ensure you have defined API_KEY in the script for the script to work")
    if debug:
        print("Using API CLIENT ID {} and API KEY {}".format(API_CLIENT_ID,API_KEY))
    a = cats.AMP(cloud="us",api_client_id=API_CLIENT_ID,api_key=API_KEY,debug=debug,logfile="")
    if (operation == "events"):
        rsp = a.events(days=days,hours=hours,minutes=minutes)
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "eventtypes"):
        rsp = a.eventTypes()
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "computers"):
        rsp = a.computers(internal_ip=internal_ip,external_ip=external_ip,hostname=hostname)
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "computerguid"):
        rsp = a.computerGUID(guid)
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "computertrajectory"):
        rsp = a.computerTrajectory(guid,search=search)
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "computerusertrajectory"):
        rsp = a.computerUserTrajectory(guid,search=search)
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "computeruseractivity"):
        rsp = a.computerUserActivity(guid,search=search)
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "eventstreams"):
        rsp = a.geteventStreams()
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "checkisolation"):
        rsp = a.checkHostIsolation(guid)
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "isolate"):
        rsp = a.startHostIsolation(guid)
        print(json.dumps(rsp,indent=4,sort_keys=True))
    if (operation == "unisolate"):
        rsp = a.stopHostIsolation(guid)
        print(json.dumps(rsp,indent=4,sort_keys=True))

if __name__ == "__main__":
    main(sys.argv[1:])
