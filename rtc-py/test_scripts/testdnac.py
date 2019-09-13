#!/usr/bin/python3
import sys
import getopt
import cats
import json


commands = [ {"description":"Get Network Objects"},
]
def print_help() :
        print("running python " + str(sys.version_info))
        name = os.path.basename(__file__)
        print("Usage: " + name + " -s server -u username -p password -c command")
        


def main(argv):
        debug = True
        server = "sandboxdnac.cisco.com"
        username = "devnetuser"
        password = "Cisco123!"
        name = "defaultname"
        value = "1.1.1.1"
        command = "1"
        try:
                opts, args = getopt.getopt(argv,"dhs:u:p:n:v:c:")
                for opt, arg in opts:
                        if opt == ("-d"):
                                debug = True
                        if opt == ("-h"):
                                phelp = True
                        if opt == ("-s"):
                                server = arg
                        if opt == ("-u"):
                                username = arg
                        if opt == ("-p"):
                                password = arg
                        if opt == ("-c"):
                                command = arg
                        if opt == ("-n"):
                                name = arg
                        if opt == ("-v"):
                                value = arg

                                
        except Exception as err:
                print("Invalid option specified")
                


        dnac = cats.DNAC(server,username,password,debug,"")
        if not dnac:
                print("Could not create DNAC object")
                sys.exit(2)


        print("created dnac")
        print(dnac.get_auth_token())
        rsp = dnac.dnac_get("network-device")

        for device in rsp["response"]:
                print("----------------------------------------------------------------")
                this_ip = device["managementIpAddress"]
                print("IP:" + this_ip)
                print(json.dumps(device,indent=4,sort_keys=True))                
                rsp = dnac.get_from_ip(this_ip)
                print(json.dumps(rsp,indent=4,sort_keys=True))
                this_id = rsp["response"]["id"]
                print("this id is {}".format(this_id))
                rsp = dnac.get_modules(this_id)
                print("modules are ")
                print(json.dumps(rsp,indent=4,sort_keys=True))
                
        sys.exit()


        if command == "0":
                postdata = {
                        "name" : name,
                        "description" : "testdesc",
                        "subType"     :"HOST",
                        "value"     :value,
                        "type" : "networkobject"
                }
                rsp = ftd.ftdpost("object/networks",postdata)
                print(json.dumps(rsp,indent=4,sort_keys=True))
                
        if command == "1":
                rsp = ftd.network_object_create(name,value)
                print(json.dumps(rsp,indent=4,sort_keys=True))                
        if command == "2":
                rsp = ftd.network_objects_get(name=name)
                print(json.dumps(rsp,indent=4,sort_keys=True))
        if command == "3":
                rsp = ftd.network_object_change_by_name(name,value)
                print(json.dumps(rsp,indent=4,sort_keys=True))
        if command == "4":
                rsp = ftd.network_object_delete_by_name(name)
                print(json.dumps(rsp,indent=4,sort_keys=True))

        if command == "5":                
                rsp = ftd.interfaces_get()
                print(json.dumps(rsp,indent=4,sort_keys=True))

        if command == "6":                
                rsp = ftd.interface_change_by_name("GigabitEthernet0/0","outside2","10.1.1.2","255.255.255.0")
                print(json.dumps(rsp,indent=4,sort_keys=True))
                
                
if __name__ == "__main__":
    main(sys.argv[1:])
    
