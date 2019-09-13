#!/usr/bin/python3
import cats
import json
from datetime import datetime
import time
import rtcdb
import sys
import _thread
import ipaddress
import getopt
import os
import rtclogger

def exception_info(err):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
    return estring

def inOurNetwork(ip):
    ###
    ### returns true if the ip (string) is in our private networks, RFC 1918
    ### TODO - add configurable option for non RFC 1918 internal networks
    
    if ipaddress.ip_address(ip) in ipaddress.ip_network("10.0.0.0/8"):
        return True
    if ipaddress.ip_address(ip) in ipaddress.ip_network("100.0.0.0/8"):
        return True
    if ipaddress.ip_address(ip) in ipaddress.ip_network("172.16.0.0/16"):
        return True
    if ipaddress.ip_address(ip) in ipaddress.ip_network("192.168.0.0/16"):
        return True
    return False
    




def RtcSW(swlogger,ancpolicy,rtcConfig,db,sw,ise_anc,pxgrid):

    # retrieve config for penalties
    threshold = rtcConfig["rtcThreshold"]
    penaltiesSW = rtcConfig["swEventsConfig"] ### HAKAN: is it called this?

    # use cats to query security events, then filter for SW_category events and put into dict
    SW_rsp = sw.searchSecurityEvents(days=0,hours=0,minutes=1,sourceip="",targetip="",wait=3) ### Time window should be shortened, and script should run as daemon
    try:
        SW_sec_events = SW_rsp["data"]["results"]
    except:
        ## no events fetched this time        
        swlogger.log_debug(3,"No events this loop")
        return
    # loop through all SW events
    for event in SW_sec_events:
# check what is direction
        internalIP = event["source"]["ipAddress"]
        if not inOurNetwork(internalIP):
            internalIP = event["target"]["ipAddress"]
            observable = event["source"]["ipAddress"] ### TO-DO based on event type, observable might be different
        else:
            observable = event["target"]["ipAddress"] ### TO-DO based on event type, observable might be different

        eventDetails = {
            'SW_first_active' : event["firstActiveTime"],
            'SW_last_active' : event["lastActiveTime"],
            'SW_source_IP' : internalIP,
            'SW_source_port' : event["source"]["port"],
            'SW_source_protocol' : event["source"]["protocol"],
            'SW_destination_IP' : observable,
            'SW_destination_port' : event["target"]["port"],
            'SW_destination_protocol' : event["target"]["protocol"],
            'SW_security_event_ID' : event["securityEventType"]
            }
        
        swlogger.log_debug(4,format(json.dumps(event)))

        # check if in our internal network, otherwise, could not care less
        
        ## findout if we are getting a penalty for this event type, otherwise dont care
        penaltyMac = 0
        for alarm in penaltiesSW:
            swlogger.log_debug(3,"eventid is {} securityEventType is {}".format(alarm["eventid"],event["securityEventType"]))
            if str(alarm["eventid"]) == str(event["securityEventType"]):
                penaltyMac += int(alarm["penalty"])
        if penaltyMac == 0:
            # no need to continue and insert events in db if penalty is 0
            continue
        
        rsp = pxgrid.getSessions(ip=internalIP)
        if rsp:
            thismac  = rsp["macAddress"]
            thisuser = rsp["userName"]
            ## Hakan, for now do track IPs if we can track MAC and user
            thisIP = internalIP            
        else:
            ## Hakan added keeping track of IPs, even if not known by pxGrid, i.e. MAC or user not found
            swlogger.log_debug(2,"IP {} not known by ISE pxgrid".format(internalIP))
            thismac = ""
            thisuser = ""
            thisIP = internalIP
            

        # check if there was an event with this observable already, for this user/mac/ip (this should be more harsh, extra penalties if observable was seen longer than x amount of time!)
        # db.getSWevents should take care of whether mac, user, ip is empty or not
        rsp = db.getSWevents(mac=thismac,user=thisuser,ip=thisIP,observable=observable)
        if not rsp["events"]:
            # this event with this observable has not happened before, so apply penalty!
            swlogger.log_debug(3,"New event found {}".format(json.dumps(eventDetails)))
            db.insertSWevent(mac=thismac,user=thisuser,ip=thisIP,observable=observable,penalty=penaltyMac,eventstring=json.dumps(eventDetails))
            # check if there is a mac address, and if so insert event in DB, update host and do ANC if needed
            if thismac:

                db.updateHost(mac=thismac,penalty=penaltyMac)

                # grab current penalties for the host
                dbresult = db.getHosts(mac=thismac)
                thishost = dbresult["hosts"][0]
                # check if penalties are equal or higher then threshold
                if int(thishost["penalty"]) >= int(threshold):
                    swlogger.log_debug(1,"Applying ANC policy for IP {} MAC {} Policy {}".format(internalIP,thismac,ancpolicy))
                    ise_anc.applyPolicy(internalIP,thismac,ancpolicy)
            # update user
            if thisuser:
                db.updateUser(user=thisuser,penalty=penaltyMac)
            if thisIP:
                db.updateIP(ip=thisIP,penalty=penaltyMac)
        else:
            swlogger.log_debug(3,"SW event from this mac/user to this observable already in DB")

# main function
def mainSW(threadName,thresholdLogLevel,logfilename):
    swlogger = rtclogger.LOGGER("SW",thresholdLogLevel,logfilename)
    swlogger.log_debug(0,"starting SW thread with log level {}".format(str(thresholdLogLevel)))
    db = rtcdb.RTCDB()
    dbresult = db.getRTCconfig()
    rtcConfig = json.loads(dbresult["configstring"])
    dbresult = db.getISEconfig()
    creds = json.loads(dbresult["configstring"])
    ISE_SERVER = creds["ise_server"]
    ISE_USERNAME = creds["ise_username"]
    ISE_PASSWORD = creds["ise_password"]
    PXGRID_CLIENT_CERT = creds["pxgrid_client_cert"]
    PXGRID_CLIENT_KEY = creds["pxgrid_client_key"]
    PXGRID_CLIENT_KEY_PASSWORD = creds["pxgrid_client_key_pw"]
    PXGRID_SERVER_CERT = creds["pxgrid_server_cert"]
    PXGRID_NODENAME = creds["pxgrid_nodename"]
    pxgrid = cats.ISE_PXGRID(server=ISE_SERVER,username=ISE_USERNAME,password=ISE_PASSWORD,debug=False,logfile="",clientcert=PXGRID_CLIENT_CERT,clientkey=PXGRID_CLIENT_KEY,clientkeypassword=PXGRID_CLIENT_KEY_PASSWORD,servercert=PXGRID_SERVER_CERT,nodename=PXGRID_NODENAME)

    # from cats.py create object to do ISE ANC's with
    ise_anc = cats.ISE_ANC(ISE_SERVER,ISE_USERNAME,ISE_PASSWORD,debug=False)
    ancpolicy = rtcConfig["rtcPolicyName"]

    # retrieve credentials
    dbresult = db.getSWconfig()
    creds = json.loads(dbresult["configstring"])

    SW_server = creds["sw_server"]  
    SW_username = creds["sw_username"]  
    SW_password = creds["sw_password"]  

    debug = False
    # Create SW object to retrieve events
    sw = cats.SW(SW_server,SW_username,SW_password,debug=debug,logfile="") 

    # create infinite loop, set to 50 seconds, smaller than the interval of one minue for which we retreive events
    while True:
        try:
            RtcSW(swlogger,ancpolicy,rtcConfig,db,sw,ise_anc,pxgrid)
            time.sleep(50)
        except Exception as err:
            swlogger.log_debug(0,exception_info(err))
            
        
def RtcUMB(umblogger,ancpolicy,rtcConfig,db,umb,amp,ise_anc,pxgrid):

    
    # retrieve config for penalties
    threshold = rtcConfig["rtcThreshold"]
    penaltiesUMB = rtcConfig["umbrellaEventsConfig"]

    # use cats to query security activity, then filter for UMB_category events and put into dict

    UMB_rsp = umb.reportSecurityActivity(days=0,hours=0,minutes=1) ### Time window should be shortened, and script should run as daemon
    umblogger.log_debug(7,"Got SecurityActivity response")
    try:
        if UMB_rsp["catsresult"] == "OK":
            UMB_activities = UMB_rsp["requests"]
        else:
            umblogger.log_debug(0,"Error in getting security report" + rsp["info"])
            return
    except Exception as err:
        umblogger.log_debug(1,"no umbrella response")
        return

    # loop through all security events, filter out the UMB_category events, add to dictionary
#    i = 0
    for activity in UMB_activities:
#        i = i+1
        umblogger.log_debug(4,"{}".format(json.dumps(activity)))
        # retrieve mac address and user for IP
        internalIP = activity["internalIp"]
        observable = activity["destination"]
        thishostname = ""
        if activity["originType"] == "Anyconnect Roaming Client":
            thishostname = activity["originLabel"]
        eventDetails = {
            'UMB_mac' : "",
            'UMB_internalIp' : internalIP,
            'UMB_externalIp' : activity["externalIp"],
            'UMB_destination' : observable,
            'UMB_datetime' : activity["datetime"],
            'UMB_category' : activity["categories"],
            'UMB_hostname' : thishostname
            }
        
        penaltiesUMB = rtcConfig["umbrellaEventsConfig"]
        penaltyMac = 0
        for alarm in penaltiesUMB:
            if alarm["event_name"] in activity["categories"]:   ### ASSUMPTION not sure of it is called "eventid", we should check
                    penaltyMac += int(alarm["penalty"])
        if penaltyMac == 0:
            continue


        rsp = pxgrid.getSessions(ip=internalIP)
        if rsp:
            thismac  = rsp["macAddress"]
            eventDetails["UMB_mac"] = thismac            
            thisuser = rsp["userName"]
            thisIP = internalIP
        else:
            thisIP = internalIP
            thismac = ""
            thisuser = ""

        rsp = db.getUMBevents(mac=thismac,user=thisuser,ip=thisIP,hostname=thishostname,observable=observable)                                                 
        if not rsp["events"]:

            # this event with this observable has not happened before, so apply penalty!
            umblogger.log_debug(2,"New event found - {},{},{},{}".format(thismac,thisIP,thisuser,json.dumps(eventDetails)))
            db.insertUMBevent(mac=thismac,user=thisuser,ip=thisIP,hostname=thishostname,observable=observable,penalty=penaltyMac,eventstring=json.dumps(eventDetails))            
            if thismac:                                                                                                   

                db.updateHost(mac=thismac,penalty=penaltyMac)
                dbresult = db.getHosts(mac=thismac)
                thishost = dbresult["hosts"][0]
                if int(thishost["penalty"]) >= int(threshold):
                    umblogger.log_debug(0,"Applying ANC policy for IP {} MAC {}".format(internalIP,thismac))
                    ise_anc.applyPolicy(internalIP,thismac,ancpolicy)
            if thisuser:
                db.updateUser(user=thisuser,penalty=penaltyMac)
            if thisIP:
                db.updateIP(ip=thisIP,penalty=penaltyMac)
            if thishostname:
                umblogger.log_debug(2,"Inserting Hostname event {} penalty {}".format(thishostname,penaltyMac))
                db.updateHostname(hostname=thishostname,penalty=penaltyMac)
                if int(thishostname["penalty"]) >= int(threshold):
                    amp.startHostIsolation(eventDetails["AMP_connector_guid"])
                else:
                    umblogger.log_debug(2,"Not Inserting Hostname event {} penalty {}".format(thishostname,penaltyMac))
                
        else:
            umblogger.log_debug(4,"Event from this mac/user to thid observable already in DB")

def mainUMB(threadname,thresholdLogLevel,logfilename):
    umblogger = rtclogger.LOGGER("UMB",thresholdLogLevel,logfilename)    
    umblogger.log_debug(0,"starting UMB thread with log level {}".format(str(thresholdLogLevel)))    
    db = rtcdb.RTCDB()
    dbresult = db.getRTCconfig()
    rtcConfig = json.loads(dbresult["configstring"])
    dbresult = db.getISEconfig()
    creds = json.loads(dbresult["configstring"])
    ISE_SERVER = creds["ise_server"]
    ISE_USERNAME = creds["ise_username"]
    ISE_PASSWORD = creds["ise_password"]
    PXGRID_CLIENT_CERT = creds["pxgrid_client_cert"]
    PXGRID_CLIENT_KEY = creds["pxgrid_client_key"]
    PXGRID_CLIENT_KEY_PASSWORD = creds["pxgrid_client_key_pw"]
    PXGRID_SERVER_CERT = creds["pxgrid_server_cert"]
    PXGRID_NODENAME = creds["pxgrid_nodename"]
    pxgrid = cats.ISE_PXGRID(server=ISE_SERVER,username=ISE_USERNAME,password=ISE_PASSWORD,debug=False,logfile="",clientcert=PXGRID_CLIENT_CERT,clientkey=PXGRID_CLIENT_KEY,clientkeypassword=PXGRID_CLIENT_KEY_PASSWORD,servercert=PXGRID_SERVER_CERT,nodename=PXGRID_NODENAME)

    # from cats.py create object to do ISE ANC's with
    ise_anc = cats.ISE_ANC(ISE_SERVER,ISE_USERNAME,ISE_PASSWORD,debug=False)
    ancpolicy = rtcConfig["rtcPolicyName"]
    dbresult = db.getUMBRELLAconfig()
    creds = json.loads(dbresult["configstring"])

    UMB_investigate_token = creds["u_investigate_token"]
    UMB_enforce_token = creds["u_enforce_token"]
    UMB_orgid = creds["u_orgid"]
    UMB_secret = creds["u_secret"]
    UMB_key = creds["u_key"]
    
    # log in to UMBRELLA
    umb = cats.UMBRELLA(investigate_token=UMB_investigate_token,enforce_token=UMB_enforce_token,key=UMB_key,secret=UMB_secret,orgid=UMB_orgid,debug=False)
    # need amp object to for host isolation from UMB
    dbresultAMP = db.getAMPconfig()
    credsAMP = json.loads(dbresultAMP["configstring"])    
    AMP_cloud = "us"
    # Hakan - currently not configurable, a todo
    AMP_api_client_id = credsAMP["amp_api_client_id"] 
    AMP_api_key = credsAMP["amp_api_key"]


    # Create AMP object to retrieve events
    amp = cats.AMP(cloud=AMP_cloud,api_client_id=AMP_api_client_id,api_key=AMP_api_key,debug=False,logfile="")
    
    while True:
        try:
            RtcUMB(umblogger,ancpolicy,rtcConfig,db,umb,amp,ise_anc,pxgrid)
            time.sleep(59)            
        except Exception as err:
            umblogger.log_debug(0,exception_info(err))            
    

        
def RtcAMP(amplogger,ancpolicy,rtcConfig,db,amp,ise_anc,pxgrid):

    # retrieve config for penalties
    threshold = rtcConfig["rtcThreshold"]
    penaltiesAMP = rtcConfig["ampEventsConfig"]  

    # use cats to query security events, then filter for AMP_category events and put into dict

    amplogger.log_debug(3,"Getting AMP events")
    AMP_rsp = amp.events(minutes=2) 
    AMP_activities = AMP_rsp["data"]

    # loop through all events, filter out interesting stuff
    for activity in AMP_activities:
        amplogger.log_debug(3,"Got AMP events")        
        # loop through network addresses (if they are there) and filling them into dict
        try:
            AMP_MAC = {}
            AMP_IP = {}
            if "network_addresses" in activity["computer"]:
                amplogger.log_debug(3,"found network address")            
                for index, item in enumerate(activity["computer"]["network_addresses"]):
                    AMP_MAC[int(index)] = item["mac"]
                    AMP_IP[int(index)] = item["ip"]
            else:
                amplogger.log_debug(3,"did not find  network address")                        
                continue
        except Exception as err:
            amplogger.log_debug(0,exception_info(err))
            continue
#            print(json.dumps(activity,indent=4,sort_keys=True))
    

        # create bool that becomes true if a new event needs to be created
        new_event = False

        # loop through different MAC addresses and create entry for each.... this should be grouped!!!

        for macAddress,index in enumerate(AMP_MAC):

            try:
                internalIP = AMP_IP[index]
                    # check if hostname input is there
                if "hostname" in activity["computer"]:
                    AMP_hostname = activity["computer"]["hostname"]
                else:
                    AMP_hostname = "no hostname found"
                # check if hash input is there
                if "file" in activity and "identity" in activity["file"]:
                    observable = activity["file"]["identity"]["sha256"] 
                else:
                    observable = "no hash found"

                # initialize penaltyMac
                penaltyMac = 0
                # loop through all alarms, check if penalties configured for that alarm and then add penalty points accordingly
                for alarm in penaltiesAMP:
                    if str(alarm["eventid"]) == str(activity["event_type_id"]):
                        penaltyMac += int(alarm["penalty"])
                if penaltyMac == 0:
                    # no need to insert if penalty 0
                    continue
                
                # create temp dictionary to send to DB
                eventDetails = {
                    'AMP_hash' : observable,
                    'AMP_connector_guid' : activity["connector_guid"],
                    'AMP_event_type' : activity["event_type"],                    
                    'AMP_date' : activity["date"],
                    'AMP_hostname' : AMP_hostname,
                    'AMP_MAC' : AMP_MAC,
                    'AMP_IP' : internalIP
                }
                amplogger.log_debug(3,json.dumps(eventDetails))
                
                if not internalIP:
                    continue
                
                rsp = pxgrid.getSessions(ip=internalIP)
                thishostname = AMP_hostname
                if rsp:
                    thismac  = AMP_MAC[index]
                    thisuser = rsp["userName"]
                    thisIP = internalIP
                else:
                    ## track this IP still...
                    amplogger.log_debug(3,"No info from pxGrid...{} ".format(internalIP) )
                    thisIP = internalIP
                    thismac = ""
                    thisuser = ""
                    
                rsp = db.getAMPevents(mac=thismac,user=thisuser,ip=thisIP,hostname=thishostname,observable=observable)
                if rsp["events"]:
                    ## event already observed, as for now no more penalties, ... 
                    pass
                else:
                    amplogger.log_debug(2,"Inserting AMP event {}".format(json.dumps(eventDetails)))
                    db.insertAMPevent(mac=thismac,user=thisuser,ip=thisIP,hostname=thishostname,observable=observable,penalty=penaltyMac,eventstring=json.dumps(eventDetails))                    
                    # check if there is a mac address, and if so insert event in DB, update host and do ANC if needed
                    if thismac:

                        db.updateHost(mac=thismac,penalty=penaltyMac)

                        # grab current penalties for the host
                        dbresult = db.getHosts(mac=thismac)
                        thishost = dbresult["hosts"][0]
                        # check if penalties are equal or higher then threshold
                        if int(thishost["penalty"]) >= int(threshold):
#                        rsp = anc.macPolicy(thishost["mac"])
# skip this check since it is causing up to 2 API calls instead of max one
                         # check if ANC was already performed, if not do ANC
                         # rsp contains an array of MACs
                            amplogger.log_debug(1,"Applying ANC policy for IP {} MAC {} Policy {}".format(internalIP,thismac,ancpolicy))
                            ise_anc.applyPolicy(internalIP,thismac,ancpolicy)
                        # update user
                    else:
                        amplogger.log_debug(3,"This mac was not defined...{}".format(thismac))
                    if thisuser:
                        amplogger.log_debug(2,"Inserting user event {} penalty {}".format(thisuser,penaltyMac))
                        db.updateUser(user=thisuser,penalty=penaltyMac)
                    if thisIP:
                        amplogger.log_debug(2,"Inserting IP event {} penalty {}".format(thisIP,penaltyMac))
                        db.updateIP(ip=thisIP,penalty=penaltyMac)
                    if thishostname:
                        amplogger.log_debug(2,"Inserting Hostname event {} penalty {}".format(thishostname,penaltyMac))
                        db.updateHostname(hostname=thishostname,penalty=penaltyMac)
                        if int(thishostname["penalty"]) >= int(threshold):
                            amp.startHostIsolation(eventDetails["AMP_connector_guid"])
                            
                    else:
                        amplogger.log_debug(2,"Not Inserting Hostname event {} penalty {}".format(thishostname,penaltyMac))
            except Exception as err:
                amplogger.log_debug(0,exception_info(err))                                        
            

def mainAMP(threadname,thresholdLogLevel,logfilename):
    amplogger = rtclogger.LOGGER("AMP",thresholdLogLevel,logfilename)
    amplogger.log_debug(0,"starting AMP thread with log level {}".format(str(thresholdLogLevel)))        
    db = rtcdb.RTCDB()
    dbresult = db.getRTCconfig()
    rtcConfig = json.loads(dbresult["configstring"])
    dbresult = db.getISEconfig()
    creds = json.loads(dbresult["configstring"])
    ISE_SERVER = creds["ise_server"]
    ISE_USERNAME = creds["ise_username"]
    ISE_PASSWORD = creds["ise_password"]
    PXGRID_CLIENT_CERT = creds["pxgrid_client_cert"]
    PXGRID_CLIENT_KEY = creds["pxgrid_client_key"]
    PXGRID_CLIENT_KEY_PASSWORD = creds["pxgrid_client_key_pw"]
    PXGRID_SERVER_CERT = creds["pxgrid_server_cert"]
    PXGRID_NODENAME = creds["pxgrid_nodename"]
    pxgrid = cats.ISE_PXGRID(server=ISE_SERVER,username=ISE_USERNAME,password=ISE_PASSWORD,debug=False,logfile="",clientcert=PXGRID_CLIENT_CERT,clientkey=PXGRID_CLIENT_KEY,clientkeypassword=PXGRID_CLIENT_KEY_PASSWORD,servercert=PXGRID_SERVER_CERT,nodename=PXGRID_NODENAME)

    # from cats.py create object to do ISE ANC's with
    ise_anc = cats.ISE_ANC(ISE_SERVER,ISE_USERNAME,ISE_PASSWORD,debug=False)
#    ancpolicy = "Quarantine"
    ancpolicy = rtcConfig["rtcPolicyName"]

    # retrieve credentials
    dbresult = db.getAMPconfig()
    creds = json.loads(dbresult["configstring"])

    AMP_cloud = "us"  # Hakan - currently not configurable, a todo
    AMP_api_client_id = creds["amp_api_client_id"] 
    AMP_api_key = creds["amp_api_key"]


    # Create AMP object to retrieve events
    amp = cats.AMP(cloud=AMP_cloud,api_client_id=AMP_api_client_id,api_key=AMP_api_key,debug=False,logfile="")

    # create infinite loop, set to 60 seconds
    while True:
        try:
            RtcAMP(amplogger,ancpolicy,rtcConfig,db,amp,ise_anc,pxgrid)
            time.sleep(30)            
        except Exception as err:
            amplogger.log_debug(0,exception_info(err))                        


def print_help():
    print("rtcMain -a <log threshold for AMP> -u <log Threshold for UMB> -s <log Thresold for SW> -f <logfilename>")
    print("log thresholds between 0 (only critical logging) and 7 (log everything)")
    print("not specifying a log threshold will cause the thread not to be started")
    print("rtcMain -h")
def main(argv):

    #options
    AMPlogThreshold = -1
    UMBlogThreshold = -1
    SWlogThreshold = -1
    logfilename = ""
    try:
        opts, args = getopt.getopt(argv,"ha:s:u:f:")
        for opt, arg in opts:
            if opt == '-h':
                print_help()
                sys.exit(2)
            if opt == ("-a"):
                AMPlogThreshold = int(arg)
            if opt == ("-s"):
                SWlogThreshold = int(arg)
            if opt == ("-u"):
                UMBlogThreshold = int(arg)
            if opt == ("-f"):
                logfilename = arg
                
    except Exception as err:
        
        print_help()
        sys.exit(2)
    
    # start threads, second parameter is log level
    try:
        if UMBlogThreshold != -1:            
            _thread.start_new_thread(mainUMB,("UMBthread",UMBlogThreshold,logfilename))
    except:
        print("Unable to start new UMB thread")

    try:
        if AMPlogThreshold != -1:
            _thread.start_new_thread(mainAMP,("AMPthread",AMPlogThreshold,logfilename))
    except:
        print("Unable to start new AMP thread")

    try:
        if SWlogThreshold != -1:
            _thread.start_new_thread(mainSW,("SWthread",SWlogThreshold,logfilename))
    except:
        print("Unable to start new SW thread")
        
    while True:
        time.sleep(1)
        
if __name__ == "__main__":
    main(sys.argv[1:])
