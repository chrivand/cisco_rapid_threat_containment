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
    if ipaddress.ip_address(ip) in ipaddress.ip_network("194.16.1.240/28"):
        return True
    return False
    


class rtcBASE():
    
    def __init__(self,name,thresholdLogLevel,logfilename):

        try:
            self.logger = rtclogger.LOGGER(name,thresholdLogLevel,logfilename)    
            self.logger.log_debug(0,"starting {} thread with log level {}".format(name,str(thresholdLogLevel)))    
            self.db = rtcdb.RTCDB()
            dbresult = self.db.getRTCconfig()
            self.rtcConfig = json.loads(dbresult["configstring"])
            self.threshold = self.rtcConfig["rtcThreshold"]        
            dbresult = self.db.getISEconfig()
            creds = json.loads(dbresult["configstring"])
            ISE_SERVER = creds["ise_server"]
            ISE_USERNAME = creds["ise_username"]
            ISE_PASSWORD = creds["ise_password"]
            PXGRID_CLIENT_CERT = creds["pxgrid_client_cert"]
            PXGRID_CLIENT_KEY = creds["pxgrid_client_key"]
            PXGRID_CLIENT_KEY_PASSWORD = creds["pxgrid_client_key_pw"]
            PXGRID_SERVER_CERT = creds["pxgrid_server_cert"]
            PXGRID_NODENAME = creds["pxgrid_nodename"]
            self.pxgrid = cats.ISE_PXGRID(server=ISE_SERVER,username=ISE_USERNAME,password=ISE_PASSWORD,debug=False,logfile="",clientcert=PXGRID_CLIENT_CERT,clientkey=PXGRID_CLIENT_KEY,clientkeypassword=PXGRID_CLIENT_KEY_PASSWORD,servercert=PXGRID_SERVER_CERT,nodename=PXGRID_NODENAME)

            self.ise_anc = cats.ISE_ANC(ISE_SERVER,ISE_USERNAME,ISE_PASSWORD,debug=False)
            self.ancpolicy = self.rtcConfig["rtcPolicyName"]
            dbresult = self.db.getUMBRELLAconfig()
            creds = json.loads(dbresult["configstring"])

            UMB_investigate_token = creds["u_investigate_token"]
            UMB_enforce_token = creds["u_enforce_token"]
            UMB_orgid = creds["u_orgid"]
            UMB_secret = creds["u_secret"]
            UMB_key = creds["u_key"]
    
            self.umb = cats.UMBRELLA(investigate_token=UMB_investigate_token,enforce_token=UMB_enforce_token,key=UMB_key,secret=UMB_secret,orgid=UMB_orgid,debug=False)

            dbresultAMP = self.db.getAMPconfig()
            credsAMP = json.loads(dbresultAMP["configstring"])    
            AMP_cloud = "us"

            AMP_api_client_id = credsAMP["amp_api_client_id"] 
            AMP_api_key = credsAMP["amp_api_key"]
            self.amp = cats.AMP(cloud=AMP_cloud,api_client_id=AMP_api_client_id,api_key=AMP_api_key,debug=False,logfile="")


            dbresultSW = self.db.getSWconfig()
            credsSW = json.loads(dbresultSW["configstring"])    
            SW_server = credsSW["sw_server"]  
            SW_username = credsSW["sw_username"]  
            SW_password = credsSW["sw_password"]
        
            self.sw = cats.SW(SW_server,SW_username,SW_password,debug=False,logfile="") 

        except Exception as err:
            self.logger.log_debug(0,self.logger.exception_info(err))
            
    def getISEcontext(self,ip):
        mac = ""
        username = ""
        rsp = self.pxgrid.getSessions(ip=ip)
        if rsp:
#            print(json.dumps(rsp,indent=4,sort_keys=True))
            if "macAddress" in rsp:
                mac  = rsp["macAddress"]
            else:
                self.logger.log_debug(2,"Username {} not known by ISE pxgrid".format(ip))                
            if "userName" in rsp:
                username = rsp["userName"]
            else:
                self.logger.log_debug(2,"Username {} not known by ISE pxgrid".format(ip))
        return (mac,username)
    
    def loopEvents(self):

        self.logger.log_debug(7,"Trying to Get Events ")
        events = self.getEvents()

        self.logger.log_debug(7,"Got Events {}".format(json.dumps(events)))
        try:
            for event in events:

                self.logger.log_debug(7,"Looping through events ")
                self.logger.log_debug(4,"Event {}".format(json.dumps(event)))                
                penaltyMac = self.getPenaltyForEvent(event)
                if penaltyMac == 0:
                    self.logger.log_debug(7,"No penalty for event")                    
                    continue

                hostnamePunished = False
                usernamePunished = False
                eventDetailsArr  = self.getInfoFromEvent(event)
                for eventDetails in eventDetailsArr:
                    '''
AMP can return a number of MAC,IP for one event
... each MAC, IP should increase penalty
... hostname should only be punished, i.e increase penalty once
... username should only be punished, i.e. increase penalty once
'''
                    thishostname = eventDetails["hostname"]
                    observable   = eventDetails["observable"]
                    thisIP       = eventDetails["ip"]
                    
                    (thismac,thisusername) = self.getISEcontext(thisIP)
                    self.logger.log_debug(4,"ISE info mac {} username {}".format(thismac,thisusername))                                    
                    if not self.isEventStored(mac=thismac,user=thisusername,ip=thisIP,hostname=thishostname,observable=observable):
                

                        self.logger.log_debug(2,"New event found - {},{},{},{}".format(thismac,thisIP,thisusername,json.dumps(eventDetails)))
                        self.storeEvent(mac=thismac,user=thisusername,ip=thisIP,hostname=thishostname,observable=observable,penalty=penaltyMac,eventstring=json.dumps(eventDetails))            
                        if thismac:                                                                                                   
                            self.db.updateHost(mac=thismac,penalty=penaltyMac)
                            dbresult = self.db.getHosts(mac=thismac)
                            thishost = dbresult["hosts"][0]
                            if int(thishost["penalty"]) >= int(self.threshold):
                                self.logger.log_debug(0,"Applying ANC policy for IP {} MAC {}".format(thisIP,thismac))
                                self.ise_anc.applyPolicy(thisIP,thismac,self.ancpolicy)
                        if thisusername and not usernamePunished:
                            self.db.updateUser(user=thisusername,penalty=penaltyMac)
                            usernamePunished = True
                        if thisIP:
                            self.db.updateIP(ip=thisIP,penalty=penaltyMac)
                        if thishostname and not hostnamePunished:
                            hostnamePunished = True
                            self.logger.log_debug(2,"Inserting Hostname event {} penalty {}".format(thishostname,penaltyMac))
                            self.db.updateHostname(hostname=thishostname,penalty=penaltyMac)

                            hostnames = self.db.getHostnames(hostname=thishostname)
                            if int(hostnames["hostnames"][0]["penalty"]) >= int(self.threshold):
                                self.amp.startHostIsolation(eventDetails["AMP_connector_guid"])
                        else:
                            self.logger.log_debug(2,"Hostname not there or already punished, Not Inserting Hostname event {} penalty {}".format(thishostname,penaltyMac))
                
                    else:
                        self.logger.log_debug(4,"Event from this mac/user/IP/hostname to this observable already in DB")
                
        except Exception as err:
            self.logger.log_debug(0,self.logger.exception_info(err))
    
        
class rtcUMB(rtcBASE):
    def __init__(self,threadname,logthreshold,logfilename):
        rtcBASE.__init__(self,threadname,logthreshold,logfilename)
        self.penalties = self.rtcConfig["umbrellaEventsConfig"]

    def getEvents(self):
        UMB_rsp = self.umb.reportSecurityActivity(days=0,hours=0,minutes=1) 
        self.logger.log_debug(7,"Got SecurityActivity response")

        if UMB_rsp["catsresult"] == "OK":
            events = UMB_rsp["requests"]
            return events
        else:
            self.logger.log_debug(0,"Error in getting security report" + rsp["info"])
            raise ValueError('Error in getting security report')

    def getPenaltyForEvent(self,event):
        total = 0
        for penalty in self.penalties:
            if penalty["event_name"] in event["categories"]:
                total += int(penalty["penalty"])
        return total
        
    def getInfoFromEvent(self,event):
        internalIP = event["internalIp"]
        observable = event["destination"]
        thishostname = ""
        if event["originType"] == "Anyconnect Roaming Client":
            thishostname = event["originLabel"]
        eventDetails = {
            'observable': observable,
            'mac' : "",
            'ip' : internalIP,
            'hostname' : thishostname,
            'username' : "",
            'UMB_externalIp' : event["externalIp"],
            'UMB_destination' : observable,
            'UMB_datetime' : event["datetime"],
            'UMB_category' : event["categories"],

            }
        eventDetailsArr = []
        eventDetailsArr.append(eventDetails)
        return (eventDetailsArr)
    
    def isEventStored(self,mac="",user="",ip="",hostname="",observable=""):
        rsp = self.db.getUMBevents(mac=mac,user=user,ip=ip,hostname=hostname,observable=observable)                      
        if rsp["events"]:
            return True
        return False
    
    def storeEvent(self,mac="",user="",ip="",hostname="",observable="",penalty=0,eventstring=""):
        self.db.insertUMBevent(mac=mac,user=user,ip=ip,hostname=hostname,observable=observable,penalty=penalty,eventstring=eventstring)

class rtcSW(rtcBASE):
    def __init__(self,threadname,logthreshold,logfilename):
        rtcBASE.__init__(self,threadname,logthreshold,logfilename)
        self.penalties = self.rtcConfig["swEventsConfig"]

    def getPenaltyForEvent(self,event):
        total = 0
        for penalty in self.penalties:
            if str(penalty["eventid"]) == str(event["securityEventType"]):
                total += int(penalty["penalty"])
        return total
    
    def getEvents(self):
        SW_rsp = self.sw.searchSecurityEvents(days=0,hours=0,minutes=1,sourceip="",targetip="",wait=3)
        try:
            events = SW_rsp["data"]["results"]
            return events
        except:
            self.logger.log_debug(3,"No events this loop")
            return []
        
    def isEventStored(self,mac="",user="",ip="",hostname="",observable=""):
        rsp = self.db.getSWevents(mac=mac,user=user,ip=ip,hostname=hostname,observable=observable)                      
        if rsp["events"]:
            return True
        return False

    def storeEvent(self,mac="",user="",ip="",hostname="",observable="",penalty=0,eventstring=""):
        self.db.insertSWevent(mac=mac,user=user,ip=ip,hostname=hostname,observable=observable,penalty=penalty,eventstring=eventstring)

    def getInfoFromEvent(self,event):
        thishostname = ""   ### not available from SW events, unless revdns?
        internalIP = event["source"]["ipAddress"]
        if not inOurNetwork(internalIP):
            internalIP = event["target"]["ipAddress"]
            observable = event["source"]["ipAddress"] ### TO-DO based on event type, observable might be different
        else:
            observable = event["target"]["ipAddress"] ### TO-DO based on event type, observable might be different
        
        eventDetails = {
            'observable': observable,
            'mac' : "",
            'ip' : internalIP,
            'hostname' : "",
            'username' : "",
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
        eventDetailsArr = []
        eventDetailsArr.append(eventDetails)
        return (eventDetailsArr)
    

class rtcAMP(rtcBASE):
    def __init__(self,threadname,logthreshold,logfilename):
        rtcBASE.__init__(self,threadname,logthreshold,logfilename)
        self.penalties = self.rtcConfig["ampEventsConfig"]  

        
    def getEvents(self):
        AMP_rsp = self.amp.events(minutes=2) 
        events = AMP_rsp["data"]
        return events

    def getPenaltyForEvent(self,event):
        total = 0
        for penalty in self.penalties:
            if str(penalty["eventid"]) == str(event["event_type_id"]):
                total += int(penalty["penalty"])
        return total
    
    def isEventStored(self,mac="",user="",ip="",hostname="",observable=""):
        rsp = self.db.getAMPevents(mac=mac,user=user,ip=ip,hostname=hostname,observable=observable)                      
        if rsp["events"]:
            return True
        return False

    def storeEvent(self,mac="",user="",ip="",hostname="",observable="",penalty=0,eventstring=""):
        self.db.insertAMPevent(mac=mac,user=user,ip=ip,hostname=hostname,observable=observable,penalty=penalty,eventstring=eventstring)

    def getInfoFromEvent(self,event):

        eventDetailsArr = []
        if "computer" in event and "hostname" in event["computer"]:
            hostname = event["computer"]["hostname"]
        else:
            hostname = "no hostname found"
        if "file" in event and "identity" in event["file"]:
            observable = event["file"]["identity"]["sha256"]
        else:
            observable = "no hash found"
        
        if "network_addresses" in event["computer"]:
            self.logger.log_debug(3,"found network address")
            for index, item in enumerate(event["computer"]["network_addresses"]):

                eventDetails = {
                    'mac' : item["mac"],
                    'ip'  : item["ip"],
                    'hostname' : hostname,
                    'username' : '',
                    'observable' : observable,
                    'AMP_connector_guid' : event["connector_guid"],
                    'AMP_event_type' : event["event_type"],                    
                    'AMP_date' : event["date"],
                    'AMP_hostname' : hostname,
                }
                eventDetailsArr.append(eventDetails)
                
        else:
            self.logger.log_debug(3,"did not find network address")
        
        return (eventDetailsArr)
    
def mainRTC(threadname,rtc):

    while True:
        try:
            rtc.loopEvents()
            time.sleep(59)                                    
        except Exception as err:
            rtc.logger.log_debug(0,rtc.logger.exception_info(err))            
            time.sleep(59)                                    
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
        logger = rtclogger.LOGGER("main",1,"/tmp/rtc.log")    
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
            rtc = rtcUMB("UMB",UMBlogThreshold,logfilename)
            _thread.start_new_thread(mainRTC,("UMB",rtc))
    except Exception as err:
        logger.log_debug(1,"Unable to start new UMB thread "+logger.exception_info(err))

    try:
        if AMPlogThreshold != -1:
            rtc = rtcAMP("AMP",AMPlogThreshold,logfilename)            
            _thread.start_new_thread(mainRTC,("AMP",rtc))
    except Exception as err:        
        logger.log_debug(1,"Unable to start new AMP thread "+logger.exception_info(err))        
    try:
        if SWlogThreshold != -1:
            rtc = rtcSW("SW",SWlogThreshold,logfilename)            
            _thread.start_new_thread(mainRTC,("SW",rtc))
    except Exception as err:        
        logger.log_debug(1,"Unable to start new SW thread "+logger.exception_info(err))                
        
    while True:
        time.sleep(1)
        
if __name__ == "__main__":
    main(sys.argv[1:])
