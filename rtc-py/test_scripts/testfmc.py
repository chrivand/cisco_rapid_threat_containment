#!/usr/bin/python3
import sys
import getopt
import cats
import json
def main(argv):
        debug = False
        try:
                opts, args = getopt.getopt(argv,"d")
                for opt, arg in opts:
                        if opt == ("-d"):
                                debug = True
        except Exception as err:
                print("Invalid option specified")
                
                

        fmcserver = "fmc.dcloud.local"
        username = "restapiuser"
        password = "C1sco12345"
        devicename="NGFW2"        
        hostname = "ngfw2.dcloud.local"
        regkey = "C1sco12345"
        
        policyname = str(input("Enter name of Access Policy to apply to new device:"))

        fmc = cats.FMC(fmcserver,username,password,debug,"")
        if not fmc:
                print("Could not create FMC object")
                sys.exit(2)
        
        rsp = fmc.add_device(devicename=devicename,hostname=hostname,regkey=regkey,policyname=policyname)
        if not rsp or rsp["catsresult"] != "OK":
                print("!!! Error in creating device! ")
                return
        if debug:
                print(json.dumps(rsp,indent=4,sort_keys=True))        
        print("...device successfully created on FMC")
        while True:
                user_input = str(input("In the FMC UI, confirm that the device discovery has completed and then press 'y' to continue or 'n' to\
 exit. [y/n]"))
                if user_input == "n":
                        print("Exiting on user request")
                        return
                if user_input == "y":
                        break
                print("Please answer 'y' or 'n'")

        ## configure interfaces

        print("...configuring GigabitEthernet0/0")
        rsp = fmc.configure_interface(devicename=devicename,ifname="ISP-Side",name="GigabitEthernet0/0",ipv4address="198.18.133.22",ipv4mask="18")
        if not rsp or rsp["catsresult"] != "OK":
                print("could not configure interface")
                return
        print("...configuring GigabitEthernet0/1")                
        rsp = fmc.configure_interface(devicename=devicename,ifname="LAN-Side",name="GigabitEthernet0/1",ipv4address="198.19.10.2",ipv4mask="24")
        if not rsp or rsp["catsresult"] != "OK":
                print("could not configure interface")
        
        print("*** Configured Interfaces! *** ")


                
if __name__ == "__main__":
    main(sys.argv[1:])
    
