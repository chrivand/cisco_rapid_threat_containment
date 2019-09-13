#!/usr/bin/python3                                                                                                                         
import json
import sys
import pprint
from time import gmtime,strftime
import datetime
import os
import getopt
import re
import cats

def print_help():
    print("running python " + str(sys.version_info))
    name = os.path.basename(__file__)
    print("Usage: " + name + " -o observable -i ip -d")
    print("print -o <observable> to inject into CTR API")
    print("print -i <ip> to get sightings for this IP address")    
    print("print -d to add debug")
    
def main(argv):

    observables = ""
    ip = ""
    debug = False
    try:
        opts, args = getopt.getopt(argv,"do:i:")
        for opt, arg in opts:
            if opt == '-h':
                print_help()
                sys.exit(2)
            if opt == ("-d"):
                debug = True
            if opt == ("-o"):
                observables = arg
            if opt == ("-i"):
                ip = arg
                
    except Exception as err:
        
        print_help()
        sys.exit(2)

    if not observables and not ip:
        print_help()
        sys.exit(2)
        
    try:
        creds = json.loads(open("ctrapi.json").read())
        print(json.dumps(creds))
        CTR_CLIENT_ID     = creds["client_id"]
        CTR_CLIENT_SECRET = creds["client_secret"]

    except Exception as e:
        print(str(e))
        print("Failed to open ctrapi.json")
        print("Ensure you have defined API key  stuff in the script for the script to work")
    if debug:
        print("Using API CTR CLIENT ID {}".format(CTR_CLIENT_ID))
        print("Using API CTR CLIENT SECRET {}".format(CTR_CLIENT_SECRET))

    ctr = cats.CTR(client_id = CTR_CLIENT_ID,client_secret=CTR_CLIENT_SECRET,debug=debug,logfile="")

    if not ctr:
        print("Could not initialize CTR")
        sys.exit(2)

    if observables:
        rsp = ctr.get_actions_observables(observables)
        print(json.dumps(rsp,indent=4,sort_keys=True))        
    if ip:
        observables = [
            {"type":"ip",
             "value":ip
             }
            ]
        rsp = ctr.get_sightings_for_observables(observables)
        print(json.dumps(rsp,indent=4,sort_keys=True))        

        for module in rsp['apirsp']['data']:
            if module['module'] == "Private AMP Global Intel":
                if 'sightings' in module['data']:
                    # store amount of sightings                                                                                                                                                      
                    total_firepower_sighting_count = module['data']['sightings']['count']
                    for target in module['data']['sightings']['docs']:
                        # also store contextual observables                                                                                                                                          
                        for item in target['targets'][0]['observables']:
                                if item['type'] == 'ip':
                                    firepower_ip_sighting = item['value']

                        for item in target['relations']:
                            if item['relation'] == "Connected_To":
                                firepower_ip_connected_to = item['source']['value']

                    # create dict to return to main script

                    for incident in  module["data"]["incidents"]["docs"]:
                        print("**********************************************")
                        print(incident["short_description"])
                        print("**********************************************")                        
                    firepower_dict = {
                        'total_firepower_sighting_count': total_firepower_sighting_count,
                        'firepower_ip_sighting': firepower_ip_sighting,
                        'firepower_ip_connected_to': firepower_ip_connected_to
                    }

                    print(firepower_dict)

if __name__ == "__main__":
    main(sys.argv[1:])
