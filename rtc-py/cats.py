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
import re
import base64
import urllib
import xml.etree.ElementTree
import xml.etree.ElementTree as ET
import ipaddress
from requests.auth import HTTPBasicAuth
import ssl

#
# CATS
# base class, from which to inherit, dealing mainly with errors, exceptions and logging
#  implements basic get, put, post, delete methods returning result to JSON
#
class CATS:

    def __init__(self,debug,logfile):
        self.debug = debug
        self.logfile = logfile

    def log_debug(self,message):
        if self.debug:
            if self.logfile:
                logfile = open(self.logfile,"a")
                logfile.write(message)
            else:
                print(message)

    def exception_handler(self,err):
        (exc_type, exc_obj, exc_tb) = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        errorstring = "Exception! {} {} {} {}\n ".format(str(err),exc_type,fname,exc_tb.tb_lineno)
        self.log_debug(errorstring)
        result = { "catsresult": "ERROR", "info": errorstring }
        return result

    def exception_refuse_init(self,err):
        (exc_type, exc_obj, exc_tb) = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        errorstring = "Exception! {} {} {} {}\n ".format(str(err),exc_type,fname,exc_tb.tb_lineno)
        self.log_debug(errorstring)
        return None
    
    def error_handler(self,err):
        self.log_debug(err)
        result = { "catsresult": "ERROR", "info": err }
        return result

    def get(self,url,headers,verify):
        try:
            self.log_debug("GET  " + url)
            self.log_debug("HEADERS " +str(headers))
            r = requests.get(url,verify=False,headers=headers)
            status_code = r.status_code
            if  (status_code / 100) == 2:
#                json_response = json.loads(r.text)
                json_response = r.json()
                result = { "catsresult": "OK", "info": "GET successful"  }
                json_response.update(result)
                return json_response
            else:
                self.log_debug(status_code)
                self.log_debug(r.text)
                errorstring = "Error in get {}".format(str(status_code))
                self.log_debug(errorstring)
                result = { "catsresult": "ERROR", "info": errorstring  }
                return result
        except Exception as err:
            self.exception_handler(err)
            return None

    def delete(self,headers,url,verify):

        try:
            self.log_debug(url)
            self.log_debug(str(headers))
            r = requests.delete(url=url,headers=headers,verify=verify)
            status_code = r.status_code
            if  (status_code == 204):
                result = { "catsresult": "OK", "info": "Delete successful" }
                return result
            else:
                self.log_debug(r.text)
                self.log_debug("Error in delete " + str(status_code))
                result = { "catsresult": "ERROR", "info": "Delete failed" }
                return result
        except Exception as err:
            return self.exception_handler(err)

    def post(self,url,headers,data,verify):

        try:
            self.log_debug("POST:   " + url)
            self.log_debug("HEADERS:" + str(headers))
            self.log_debug("DATA:   " + data)
            r = requests.post(url,data=data,headers=headers,verify=verify)
            if r.status_code // 100 == 2:
                if "Set-Cookie" in r.headers:
                    if r.headers["Set-Cookie"][:]:                
                        self.cookie = r.headers["Set-Cookie"][:]                
                result = { "catsresult": "OK", "info": "POST successful"  }
                rsp = json.loads(r.text)
                result.update({"apirsp":rsp})
                return result
            else:
                errorstring = "invalid return code: {} - {}".format(str(r.status_code),r.text)
                return(self.error_handler(errorstring))
        except Exception as err:
            return(self.exception_handler(err))

    def put(self,headers,url,data,verify=False):

        try:
            self.log_debug("PUT:" +url)
            self.log_debug("PUT:" +data)            
            r = requests.put(url=url,headers=headers,data=data,verify=verify)
            status_code = r.status_code
            if  (status_code // 100) == 2:
                result = {"catsresult":"OK"}
                return result
            else:
                self.log_debug(r.text)                
                errorstring = "Error in PUT , status code: " + str(status_code)
                result = {"catsresult":"ERROR","info": errorstring}
                return result
        except Exception as err:
            self.exception_handler(err)

#
#   Class implementing parts of Cisco DNA Center API
#
#
class DNAC(CATS):
    
    def __init__(self,controller_ip, username, password,debug,logfile):
        CATS.__init__(self,debug,logfile)
        self.controller_ip = controller_ip
        login_url = "https://{0}/dna/system/api/v1/auth/token".format(controller_ip)

        
        result = requests.post(url=login_url, auth=HTTPBasicAuth(username,password), verify=False)
## todo inconsistent error handling
        result.raise_for_status()        
        token = result.json()["Token"]
        self.auth_token =  {
            "controller_ip": controller_ip,
            "token": token
        }

    def get_auth_token(self):
        return self.auth_token

    def dnac_get(self,path):
        url = "https://{}/api/v1/{}".format(self.controller_ip,path)
        headers = {'X-auth-token' : self.auth_token["token"]}
        return(self.get(url,headers,verify=False))

    def get_from_ip(self,ip):
        return(self.dnac_get("network-device/ip-address/{}".format(ip)))

    def get_modules(self,this_id):
        return self.dnac_get("network-device/module?deviceId={}".format(this_id))
    
#   Class implementing parts of FTD API
#
#
class FTD(CATS):
    
    def __init__(self,host,username,password,debug,logfile):
        
        CATS.__init__(self,debug,logfile)
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization':'Bearer'
        }
        path = "/api/fdm/v1/fdm/token"
        self.server = "https://"+host
        url = self.server + path
        body = {
            "grant_type" : "password",
            "username"   : username,
            "password"   : password,
            }
        self.access_token = ""
        self.refresh_token = ""

        try:
            rsp = self.post(url, headers=self.headers,data=json.dumps(body), verify=False)
            if rsp["catsresult"] == "OK":
                self.access_token = rsp["apirsp"]["access_token"]
                self.headers["Authorization"] = "Bearer {}".format(self.access_token)
                self.refresh_token = rsp["apirsp"]["refresh_token"]
            else:
                log_debug("Could not create FTD object {} {}".format(rsp["catsresult"],rsp["info"]))
                return None
            
        except Exception as err:
            self.exception_refuse_init(err)
            return None
    def ftdget(self,api):
        api_path= "/api/fdm/v1" + api
        url = self.server+api_path
        return (self.get(url=url,headers=self.headers,verify=False))
        
    def ftdpost(self,api,post_data):
        api_path= "/api/fdm/v1/" + api
        url = self.server+api_path
        return (self.post(url=url,data=json.dumps(post_data),headers=self.headers,verify=False))

    def ftdput(self,api,data):
        api_path= "/api/fdm/v1/" + api
        url = self.server+api_path
        return (self.put(url=url,data=json.dumps(data),headers=self.headers,verify=False))
    
    def ftddelete(self,api):
        api_path= "/api/fdm/v1/" + api
        url = self.server+api_path
        return (self.delete(url=url,headers=self.headers,verify=False))
    
    def get_access_token(self):
        return self.access_token

    def find_item(self,rsp,nametosearch,thisname):
        self.log_debug(" {}  {} ".format(nametosearch,thisname))
        for item in rsp["items"]:
            if item[nametosearch] == thisname:
                return(item)

        return(None)
        
    def interfaces_get(self,name=""):
        return (self.ftdget("/devices/default/interfaces?limit=10000"))

    def interface_change_by_name(self,hardwarename,ifname,ipv4address,ipv4mask):
        putdata = {
            "description": "kalle",
            "duplexType": "AUTO",
            "enabled": True,
            "gigabitInterface": True,
            "hardwareName": "GigabitEthernet0/0",
#            "id": "8d6c41df-3e5f-465b-8e5a-d336b282f93f",
            "ipv4": {
                "addressNull": False,
                "defaultRouteUsingDHCP": False,
                "dhcp": False,
                "ipAddress": {
                    "ipAddress": ipv4address,
                    "netmask": ipv4mask,
                    "type": "ipv4address"
                },
                "ipType": "STATIC",
                "type": "interfaceipv4"
            },
            "ipv6": {
                "autoConfig": True,
                "dadAttempts": 1,
                "dhcpForManagedConfig": False,
                "dhcpForOtherConfig": False,
                "enableRA": False,
                "enabled": True,
                "ipAddresses": [],
#                "linkLocalAddress": {
#                    "ipAddress": null,
#                    "type": "ipv6address"
#                },
                "prefixes": [],
                "type": "interfaceipv6"
            },
            "linkState": "UP",
#            "links": {
#                "self": "https://198.18.133.8/api/fdm/v1/devices/default/interfaces/8d6c41df-3e5f-465b-8e5a-d336b282f93f"
#            },
            "managementInterface": False,
            "managementOnly": False,
            "mtu": 1500,
            "name": "outside",
            "speedType": "AUTO",
            "subInterfaces": [],
            "tenGigabitInterface": False,
            "type": "physicalinterface",
            "version": ""
        }

        rsp = self.interfaces_get()
        self.log_debug(json.dumps(rsp,indent=4,sort_keys=True))
        if rsp["catsresult"] == "OK":
            found_item = self.find_item(rsp=rsp,nametosearch="hardwareName",thisname=hardwarename)
            if found_item:
                putdata["id"] = found_item["id"]
                putdata["version"] = found_item["version"]
                
                return(self.ftdput(api="devices/default/interfaces/{}".format(found_item["id"]),data=putdata))
            else:
                result = {"catsresult":"ERROR","info": "could not find {} for changing".format(hardwarename)}                    
        else:
            result = {"catsresult":"ERROR","info": "could not delete {}".format(hardwarename)}
        return result
        
        
    def network_object_create(self,name,value):

        if '/' in value:
            self.log_debug("found /")
            subType = "NETWORK"
        else:
            self.log_debug("not found /")
            subType = "HOST"
            
        postdata = {
            "name" : name,
            "description" : "testdesc",
            "subType"     :subType,
            "value"     :value,
            "type" : "networkobject"
        }
        return(self.ftdpost("object/networks",postdata))

    def network_objects_get(self,name=""):
        return (self.ftdget("/object/networks?limit=10000"))

    def network_object_delete_by_name(self,name):
        rsp = self.network_objects_get()
        if rsp["catsresult"] == "OK":
            found_item = find_item(rsp,"name",name)
            if found_item:
                return(self.ftddelete(api="object/networks/{}".format(found_item["id"])))
            else:
                result = {"catsresult":"ERROR","info": "could not find {} for deletion".format(name)}                    
        else:
            result = {"catsresult":"ERROR","info": "could not delete {}".format(name)}
        return result
    
    def network_object_change_by_name(self,name,value):

        putdata = {
            "name": name,
            "description": "string",
            "subType": "HOST",
            "value": value,
            "type": "networkobject",
            "version": "",
        }
        
        rsp = self.network_objects_get()

        if rsp["catsresult"] == "OK":
            found_id = None
            for item in rsp["items"]:
                if item["name"] == name:
                    found_id = item["id"]
                    found_version = item["version"]
                    break
            if found_id:
                putdata["id"] = found_id
                putdata["version"] = found_version
                return(self.ftdput(api="object/networks/{}".format(found_id),data=putdata))
            else:
                result = {"catsresult":"ERROR","info": "could not find {} for changing".format(name)}                    
        else:
            result = {"catsresult":"ERROR","info": "could not change {}".format(name)}
        return result

    #
    
    
#   Class implementing pars of FMC API
#
#
class FMC(CATS):
    
    def __init__(self,host,username,password,debug,logfile):
        
        CATS.__init__(self,debug,logfile)
        self.headers = {'Content-Type': 'application/json'}
        path = "/api/fmc_platform/v1/auth/generatetoken"
        self.server = "https://"+host
        url = self.server + path
        try:
            r = requests.post(url, headers=self.headers, auth=requests.auth.HTTPBasicAuth(username,password), verify=False)
            auth_headers = r.headers
            token = auth_headers.get('X-auth-access-token', default=None)
            self.uuid = auth_headers.get('DOMAIN_UUID', default=None)
            self.headers['X-auth-access-token'] = token
            if token == None:
                self.log_debug("No Token found, I'll be back terminating....")
                return None
        except Exception as err:
            self.exception_refuse_init(err)
            return 
        
    def fmcget(self,api):
        api_path= "/api/fmc_config/v1/domain/" + self.uuid + api
        url = self.server+api_path
        return (self.get(url=url,headers=self.headers,verify=False))

    def fmcpost(self,api,post_data):
        api_path= "/api/fmc_config/v1/domain/" + self.uuid + api
        url = self.server+api_path
        return (self.post(url=url,data=post_data,headers=self.headers,verify=False))

    def fmcput(self,api,put_data):
        api_path= "/api/fmc_config/v1/domain/" + self.uuid + api
        url = self.server+api_path
        return (self.put(url=url,data=put_data,headers=self.headers,verify=False))

    def configure_interface(self,devicename,ifname,name,ipv4address,ipv4mask):
        rsp = self.fmcget(api="/devices/devicerecords")
        device_id = ""
        for device in rsp["items"]:
            if device["name"] == devicename:
                device_id = device["id"]
        if not device_id:
            self.log_debug("Weird, could not find our new device {0}".format(devicename))
            result = {"catsresult":"Error", "info":"could not add new device"}
            return result
        rsp = self.fmcget(api="/devices/devicerecords/" + device_id + "/physicalinterfaces")
        interface_id = ""
        for interface in rsp["items"]:
            if interface["name"] == name:
                interface_id = interface["id"]

        if not interface_id:
            result = {"catsresult":"Error", "info":"could not find interface"}                
            return result
            
        interface_put = {
            "type": "PhysicalInterface",
            "hardware": {
                "duplex": "AUTO",
                "speed": "AUTO"
            },
            "mode": "NONE",
            "enabled": True,
            "MTU": 1500,
            "managementOnly": False,
            "ifname": ifname,
            "enableAntiSpoofing": False,
            "name": name,
            "id": interface_id,
            "ipv4" : {
                "static": {
                    "address":ipv4address,
                    "netmask":ipv4mask
                }
            }
        }
        put_data = json.dumps(interface_put)
        return(self.fmcput(api="/devices/devicerecords/"+device_id+"/physicalinterfaces/"+interface_id,put_data=put_data))

        
    def add_device(self,devicename,hostname,regkey,policyname):
                
        self.log_debug("...checking if Access Policy {0} is defined on FMC".format(policyname))
        rsp = self.fmcget(api="/policy/accesspolicies")
        items = rsp["items"]

        policy_id = ""
        for item in items:
            if item["name"] == policyname:
                policy_id = item["id"]
        if not policy_id:
            self.log_debug("!!!Could not find policy {0}!".format(policyname))
            result = {"catsresult" : "Error", "info": "Could not find the policy"}
            return result
        device_post = {
            "name": devicename,
            "hostName": hostname,
            "regKey": regkey,
            "type": "Device",
            "license_caps": [
                "BASE",
                "MALWARE",
                "URLFilter",
                "THREAT"
            ],
            "accessPolicy": {
                "id": policy_id
            }
        }
        post_data = json.dumps(device_post)
        return(self.fmcpost(api="/devices/devicerecords",post_data=post_data))
            
#
#   Class implementing parts of SW api
#
class SW(CATS):

    
## define structure for complex operation, first a post to initate search, then subsequent queries to see if search done, then fetch result
    API_BASE = "/sw-reporting/v1"
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

    def __init__(self,server,username,password,debug=False,logfile=""):

        CATS.__init__(self,debug,logfile)

        self.server = server
        self.username = username
        self.password = password
        self.tenantid = ""
        self.cookie   = ""
        try:

            url = "https://{}/token/v2/authenticate".format(server)
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = "username={}&password={}".format(username,password)
            rsp = self.post(url=url,headers=headers,data=data,verify=False)
            if rsp["catsresult"] == "OK":
                pass
            else:
                return(rsp)

            url = "https://{}{}/tenants".format(self.server,self.API_BASE)

            headers = {
                 "Content-Type":"application/json",
                 "Cookie": self.cookie
            }

            rsp = self.get(url=url,headers=headers,verify=False)
            self.tenantid = str(rsp["data"][0]["id"])
            self.log_debug("tenantid: " + self.tenantid)
        except Exception as err:
            self.exception_handler(err)
    

            
    def eventList(self):
        

        url = "https://{}/sw-reporting/v1/tenants/{}/security-events/templates".format(self.server,self.tenantid)
        headers = {
            "Content-Type":"application/json",
                    "Cookie": self.cookie
        }
        return (self.get(url=url,headers=headers,verify=False))
        
    
            
    def getSWpath(self,path,tag=""):

        headers = {
            "Content-Type":"application/json",
                    "Cookie": self.cookie
        }

        if self.tenantid:
            if tag:
                url = "https://{}{}{}".format(self.server,API_BASE,path.format(self.tenantid,tag))
#                url = "https://" + self.server  + self.API_BASE + path.format(self.tenantid,tag)
            else:
                url = "https://{}{}{}".format(self.server,self.API_BASE,path.format(self.tenantid))
        else:
            url = "https://{}{}{}".format(self.server,self.API_BASE,path)

        return (self.get(url,headers=headers,verify=False))
    
    def postSWdata(self,path,data):

        headers = {
                    "Content-Type":"application/json",
                    "Cookie": self.cookie
        }
        url = "https://{}{}{}".format(self.server,self.API_BASE,path)
        jsondata = json.dumps(data)
        return (self.post(url=url,headers=headers,data=jsondata,verify=False))
            
    def search(self,search,data,wait=3):
        headers = {
                    "Content-Type":"application/json",
                    "Cookie": self.cookie
        }
        found = False
        for s in self.API_SEARCHES:
            if s["id"] == search:
                postpath = s["postpath"]
                querypath = s["querypath"]
                resultpath = s["resultpath"]
                found = True
        if not found:
            self.log_debug("Illegal operation - shold not happen")
            return None

        apipath =  postpath.format(self.tenantid)

        try:
            percentcomplete = "not returned"
            rsp = self.postSWdata(apipath,data)

# insane? the parameters returned to specify job status and job id have different JSON locations"
#  --- requiring insane logig below
            if search == "secevents":
                jobstatus  = rsp["apirsp"]["data"]["searchJob"]["searchJobStatus"]
                jobid      = rsp["apirsp"]["data"]["searchJob"]["id"]
                percentcomplete = rsp["apirsp"]["data"]["searchJob"]["percentComplete"]
            else:
                jobstatus  = rsp["apirsp"]["data"]["status"]
                jobid = rsp["apirsp"]["data"]["queryId"]
                percentcomplete = "not returned"
            self.log_debug("JOBSTATUS:" + jobstatus)
            self.log_debug("JOBID    :" + str(jobid))
            self.log_debug("PERCENT  :" + str(percentcomplete))
#        url = "https://{}{}{}".format(self.server,self.API_BASE,path)
#temp ugly below
            querypath =  querypath.format(self.tenantid,jobid)
            querypath = "https://" + self.server + self.API_BASE + querypath
            resultpath =  resultpath.format(self.tenantid,jobid)
            resultpath= "https://" + self.server + self.API_BASE + resultpath
            while True:
                time.sleep(wait)
                rsp = self.get(url=querypath,headers=headers,verify=False)
                jobstatus = rsp["data"]["status"]

                if jobstatus == "COMPLETED":
                    rsp = self.get(url=resultpath,headers=headers,verify=False)
                    return rsp

        except Exception as err:
            self.exception_handler(err)

    def searchSecurityEvents(self,days=0,hours=0,minutes=0,sourceip="",targetip="",wait=3):
#
#  weird, different time format reuired for flow reports compated to security events
#

        time_to = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        time_from = (datetime.utcnow() - timedelta(days=int(days),hours = int(hours),minutes=int(minutes))).strftime('%Y-%m-%dT%H:%M:%SZ')

        seceventids = []
        body = {
            "securityEventTypeIds": seceventids,
            "timeRange": {
            "from": time_from,
            "to": time_to
            },
        }
        if sourceip or targetip:
            hosts = []
            index = 0
            if sourceip:
                t = { "ipAddress": sourceip,"type":"source"}
                hosts.append(t)
            if targetip:
                t = { "ipAddress": targetip,"type":"target"}
                hosts.append(t)
            body.update({"hosts":hosts})
        rsp = self.search("secevents",body,wait)
        return rsp

    
    def searchFlowReports(self,operation,days,hours,sourceip,targetip,wait):
#
#  weird, different time format reuired for flow reports compated to security events
#
        
        time_to = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        temp_t = (datetime.utcnow() - timedelta(days=days,hours = hours))
        time_from = temp_t.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = {
            "startTime": time_from,
            "endTime": time_to,
        }
        if sourceip:
            subject = { "ipAddresses": { "includes": [sourceip],"excludes":[] } } 
            body.update({"subject":subject})
        if targetip:
            peer = { "ipAddresses": { "includes": [targetip],"excludes":[] } } 
            body.update({"peer":peer})
            
        rsp = self.search(operation,body,wait)
        return rsp

    def flowsFromIP(self,ipaddress,days=0,hours=1,minutes=0):

        duration = days * 24 * 60 * 60 + hours*60*60 + minutes*60
        txml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        txml += "<soapenc:Envelope xmlns:soapenc=\"http://schemas.xmlsoap.org/soap/envelope/\">\n"
        txml += "\t<soapenc:Body>\n"
        txml += "\t\t<getFlows>\n"
        txml += "\t\t\t<flow-filter max-rows=\"10000\" domain-id=\"{}\" remove-duplicates=\"true\" order-by=\"TOTAL_BYTES\" include-interface-data=\"false\">\n".format(self.tenantid)
        txml += "\t\t\t\t<date-selection>\n"
        txml += "\t\t\t\t\t<time-window-selection duration=\"{}\"/>\n".format(duration)
        txml += "\t\t\t\t</date-selection>\n"
        txml += "\t\t\t\t<host-selection>\n"
        txml += "\t\t\t\t\t<host-pair-selection direction=\"BETWEEN_SELECTION_1_SELECTION_2\">\n"
        txml += "\t\t\t\t\t\t<selection-1>\n"
        txml +=  "<ip-address-range-selection value=\"{}\" />".format(ipaddress)

        txml += "\t\t\t\t\t\t</selection-1>\n"
        txml += "\t\t\t\t\t</host-pair-selection>\n"
        txml += "\t\t\t\t</host-selection>\n"
#        txml += "\t\t\t\t<ports exclude=\"false\">53/udp</ports>\n"
#        txml += "\t\t\t\t<traffic>\n"
#        txml += "\t\t\t\t\t<client>\n"
#        txml += "\t\t\t\t\t\t<packets-range low-value=\"1\" />\n"
#        txml += "\t\t\t\t\t</client>\n"
#        txml += "\t\t\t\t\t<server>\n"
#        txml += "\t\t\t\t\t\t<packets-range low-value=\"1\" />\n"
#        txml += "\t\t\t\t\t</server>\n"
#        txml += "\t\t\t\t</traffic>\n"
        txml += "\t\t\t</flow-filter>\n"
        txml += "\t\t</getFlows>\n"
        txml += "\t</soapenc:Body>\n"
        txml += "</soapenc:Envelope>"
        url  = "https://{}/smc/swsService/flows".format(self.server)
        auth = HTTPBasicAuth(self.username,self.password)

        self.log_debug(url)
        self.log_debug(auth)
        self.log_debug(xml)
        try:
            r = requests.post(url=url, auth=auth, data=txml, verify=False)
            if r.status_code >= 200 and r.status_code < 300:
                rxml = r.text
                self.log_debug(rxml)

                root = xml.etree.ElementTree.fromstring(rxml.encode('ascii', 'ignore'))
                rsp   = {}
                flows = []
                for flow in root.findall('.//{http://www.lancope.com/sws/sws-service}flow'):
                    client = flow.find('.//{http://www.lancope.com/sws/sws-service}client')
                    server = flow.find('.//{http://www.lancope.com/sws/sws-service}server')

                    tstr = {
                        "id":flow.get("id"),
                        "start-time":flow.get('start-time'),
                        "last-time":flow.get('last_time'),
                        "protocol": flow.get('protocol'),
                        "total_bytes": flow.get('total-bytes'),
                        "client" : {
                            "ip": client.get('ip-address'),
                            "port": client.get('port'),
                            "host_groups": client.get('host-group-ids'),
                            "host_name":  client.get('host-name'),
                            "country": client.get('country'),
                            "bytes": client.get("bytes")
                        },
                        "server": {
                            "ip":  server.get('ip-address'),
                            "port": server.get('port'),
                            "host_groups": server.get('host-group-ids'),
                            "host_name":  server.get('host-name'),
                            "country": server.get('country'),
                            "bytes": server.get("bytes")

                        },
                    }
                    flows.append(tstr)
                rsp.update({"flows":flows})
                return rsp
            else:
                errorstring = "SMC Connection Failure - HTTP Return Code: {} Response: {}".format(str(response.status_code), response.json())
                return(self.error_handler(errorstring))

        except Exception as err:
            return(self.exception_handler('Unable to post to the SMC - Error: {}'.format(err)))

            
class TG(CATS):

    def __init__(self,api_key,debug,logfile):
        CATS.__init__(self,debug,logfile)
        self.api_key       = api_key


    def searchTG(self,url,days=30,hours=0):
        headers = {}
        before = (datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ")
        after  = (datetime.utcnow()-timedelta(days=days,hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = "{}&before={}&after={}".format(url,before,after)

        return (self.get(url=url,headers=headers,verify=True))

    def searchDomain(self,domain,days=30,hours=0):

        url = "https://panacea.threatgrid.com/api/v2/iocs/feeds/domains?api_key={}&domain={}".format(self.api_key,domain)
        return (self.searchTG(url=url,days=days,hours=hours))

    def searchIP(self,ip,days=30,hours=0):

        url = "https://panacea.threatgrid.com/api/v2/iocs/feeds/ips?api_key={}&ip={}".format(self.api_key,ip)
        return (self.searchTG(url=url,days=days,hours=hours))

    def searchURL(self,url,days=30,hours=0):

        url = "https://panacea.threatgrid.com/api/v2/iocs/feeds/urls?api_key={}&url={}".format(self.api_key,url)
        return (self.searchTG(url=url,days=days,hours=hours))



    

class AMP(CATS):

    def __init__(self,cloud,api_client_id,api_key,debug=False,logfile=""):
        CATS.__init__(self,debug,logfile)
        self.api_client_id = api_client_id
        self.api_key       = api_key
        self.api_url = "https://api.amp.cisco.com"
        if cloud=="eu":
            self.api_url ="https://api.eu.cisco.com"
        if cloud=="apjc":
            self.api_url ="https://api.apjc.cisco.com"

    def apirequest(self,apicall):
    
        headers = {"ACCEPT":"application/json","Content-Type":"application/json","Authorization":""}
        bencode = base64.b64encode((self.api_client_id + ":" + self.api_key).encode())
        headers["Authorization"] = "Basic " + bencode.decode()
        url = self.api_url + apicall
        
        return(self.get(url=url,headers=headers,verify=False))

    def apiputrequest(self,apicall):
    
        headers = {"ACCEPT":"application/json","Content-Type":"application/json","Authorization":""}
        bencode = base64.b64encode((self.api_client_id + ":" + self.api_key).encode())
        headers["Authorization"] = "Basic " + bencode.decode()
        url = self.api_url + apicall
        
        return(self.put(url=url,headers=headers,data="",verify=False))

    def apideleterequest(self,apicall):
    
        headers = {"ACCEPT":"application/json","Content-Type":"application/json","Authorization":""}
        bencode = base64.b64encode((self.api_client_id + ":" + self.api_key).encode())
        headers["Authorization"] = "Basic " + bencode.decode()
        url = self.api_url + apicall
        
        return(self.delete(url=url,headers=headers,verify=False))
    
    def events(self,days=1,hours=0,minutes=0,detection_sha256="",application_sha256="",connector="",group="",event_type=[]):

        api_call = "/v1/events/"
        start_date = (datetime.utcnow() - timedelta(days=days,hours = hours,minutes=minutes)).strftime('%Y-%m-%dT%H:%M:%S') + "+00:00"

        query = {}
        query.update({"start_date": start_date})
        if detection_sha256:
            query.update({"detection_sha256": detection_sha256})
        if application_sha256:
            query.update({"application_sha256": application_sha256})

        querystring = urllib.parse.urlencode(query)
        api_call = api_call + "?" + querystring
        rsp = self.apirequest(api_call)
        return rsp

    def eventTypes(self):
        api_call = "/v1/event_types"
        rsp = self.apirequest(api_call)
        return rsp
        
    def computers(self,internal_ip="",external_ip="",hostname="",):

        api_call = "/v1/computers/"
        query = {}
        if internal_ip:
            query.update({"internal_ip":internal_ip})
        if external_ip:
            query.update({"external_ip":external_ip})
        if hostname:
            query.update({"hostname[]":hostname})

        querystring = urllib.parse.urlencode(query)
        api_call = api_call + "?" + querystring
        rsp = self.apirequest(api_call)
        return rsp

    def computerGUID(self,guid):

        api_call = "/v1/computers/{}".format(guid)
        rsp = self.apirequest(api_call)
        return rsp


    def computerTrajectory(self,guid,search=""):
### optional search par to search for ip, sha etc (like in console
###
        api_call = "/v1/computers/{}/trajectory".format(guid)
        if search:
            query = {}
            query.update({"q":search})
            querystring = urllib.parse.urlencode(query)
            api_call = api_call + "?" + querystring
            
        rsp = self.apirequest(api_call)
        return rsp

    def computerUserTrajectory(self,guid,search=""):
### optional search par to search for ip, sha etc (like in console
###
        api_call = "/v1/computers/{}/user_trajectory".format(guid)
        if search:
            query = {}
            query.update({"q":search})
            querystring = urllib.parse.urlencode(query)
            api_call = api_call + "?" + querystring
            
        rsp = self.apirequest(api_call)
        return rsp

    def computerUserActivity(self,guid,search=""):
### optional search par to search for ip, sha etc (like in console
###
        api_call = "/v1/computers/{}/user_trajectory".format(guid)
        if search:
            query = {}
            query.update({"q":search})
            querystring = urllib.parse.urlencode(query)
            api_call = api_call + "?" + querystring
            
        rsp = self.apirequest(api_call)
        return rsp

    def eventStreams(self):

        api_call = "/v1/event_streams/"
        rsp = self.apirequest(api_call)
        return rsp

    def checkHostIsolation(self,guid):

        api_call = "/v1/computers/{}/isolation".format(guid)
        rsp = self.apirequest(api_call)
        return rsp

    def startHostIsolation(self,guid):
          # Format the URL to isolate endpoint
        api_call = "/v1/computers/{}/isolation".format(guid)
        rsp = self.apiputrequest(api_call)
        return rsp

    def stopHostIsolation(self,guid):
          # Format the URL to isolate endpoint
        api_call = "/v1/computers/{}/isolation".format(guid)
        rsp = self.apideleterequest(api_call)
        return rsp


class UMBRELLA(CATS):

    def __init__(self,investigate_token="",enforce_token="",key="",secret="",orgid="",debug=False,logfile=""):
        CATS.__init__(self,debug,logfile)
        self.investigate_token = investigate_token
        self.enforce_token = enforce_token        
        self.key = key 
        self.secret = secret
        self.orgid = orgid
        

    def listEnforcement(self):

        headers = {'Content-Type': 'application/json'}
        url = "https://s-platform.api.opendns.com/1.0/domains?customerKey={}".format(self.enforce_token)

        return(self.get(headers=headers,url=url,verify=True))
               
    def deleteEnforcement(self,domain):
        headers = {'Content-Type': 'application/json'}

        url = "https://s-platform.api.opendns.com/1.0/domains/{}?customerKey={}".format(domain,self.enforce_token)
        return (self.delete(url=url,headers=headers,verify=True))


    def addEnforcement(self,domain,url):
        headers = {'Content-Type': 'application/json'}
        pdata = {
            "alertTime": strftime("%Y-%m-%dT%H:%M:%S.0Z",gmtime()),
            "deviceVersion": "13.7a",
            "deviceId": "ba6a59f4-e692-4724-ba36-c28132c761de",
            "dstDomain": domain,
            "dstUrl": url,
            "eventTime": strftime("%Y-%m-%dT%H:%M:%S.0Z",gmtime()),
            "protocolVersion": "1.0a",
            "providerName": "Hacke Labrats"
        }
        url = "https://s-platform.api.opendns.com/1.0/events?customerKey={}".format(self.enforce_token)
        return(self.post(url,headers=headers,data=json.dumps(pdata),verify=True))
                  
    def report_get(self,url):
        headers = {}
        key = self.key
        secret = self.secret
        toencode = key + ":" + secret
        bencoded = base64.b64encode(toencode.encode())
        headers["Authorization"] = "Basic " + bencoded.decode()

        return(self.get(headers=headers,url=url,verify=True))

    def reportSecurityActivity(self,days=0,hours=1,minutes=0):
        headers = {}

        time_to = datetime.utcnow()
        time_from = datetime.utcnow() - timedelta(days=int(days),hours = int(hours),minutes=int(minutes))
        s1 = str(time_from.timestamp())
        start = str(time_from.timestamp())[:-7]
        s2 = str(time_to.timestamp())
        stop = str(time_to.timestamp())[:-7]
        url = "https://reports.api.umbrella.com/v1/organizations/{}/security-activity?start={}&stop={}".format(self.orgid,start,stop)
#        url = "https://reports.api.umbrella.com/v1/organizations/{}/security-activity".format(self.orgid)
        return(self.report_get(url=url))

    def reportDestinationIdentities(self,domain):
    
        url = "https://reports.api.umbrella.com/v1/organizations/{}/destinations/{}/identities".format(self.orgid,domain)
        return(self.report_get(url=url))
    def reportDestinationActivity(self,domain):
    
        url = "https://reports.api.umbrella.com/v1/organizations/{}/destinations/{}/activity".format(self.orgid,domain)
        return(self.report_get(url=url))

    def investigate_get(self,url):
        headers = {
             'Authorization': 'Bearer ' + self.investigate_token
        }
        return self.get(headers=headers,url=url,verify=True)

    def investigateCategories(self,domain):
        url = "https://investigate.api.opendns.com/domains/categorization/{}/?showLabels".format(domain)
        return self.investigate_get(url=url)

    def investigateDNSDB(self,domain):
        url = "https://investigate.api.opendns.com/dnsdb/name/a/{}".format(domain)
        return self.investigate_get(url=url)

    def investigateTimeline(self,domain):
        url = "https://investigate.api.opendns.com/timeline/{}".format(domain)
        return self.investigate_get(url=url)

    def investigateIP(self,ip):
        url = "https://investigate.api.opendns.com/dnsdb/ip/a/{}".format(ip)
        return self.investigate_get(url=url)

    def investigateIPlatestDomains(self,ip):
        url = "https://investigate.api.opendns.com/ips/{}/latest_domains".format(ip)
        return self.investigate_get(url=url)

    def investigateIPtimeline(self,ip):
        url = "https://investigate.api.opendns.com/timeline/{}".format(ip)
        return self.investigate_get(url=url)

    def investigateSample(self,hash):
        url = "https://investigate.api.opendns.com/sample/{}".format(hash)
        return self.investigate_get(url=url)
  

class CTR(CATS):

    def __init__(self,client_id,client_secret,debug=False,logfile=""):
        CATS.__init__(self,debug,logfile)        
        self.client_id = client_id
        self.client_secret = client_secret
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }

        data = {
            'grant_type': 'client_credentials'
        }
        try:
            response = requests.post('https://visibility.amp.cisco.com/iroh/oauth2/token', headers=headers, data=data, auth=(client_id, client_secret))
    
            if response.status_code == 200:
                rsp_dict = json.loads(response.text)
                self.access_token = (rsp_dict['access_token'])
                self.scope = (rsp_dict['scope'])
                self.expiration_time = (rsp_dict['expires_in'])
                return None
            else:
                self.log_debug("Access token request failed, status code: {response.status_code}")
                return None
        except Exception as err:
            return self.exception_refuse_init(err)

    def get_observables(self,raw_text):

        bearer_token = 'Bearer ' + self.access_token
        headers = {
            'Authorization': bearer_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = json.dumps({"content":raw_text})
        return (self.post('https://visibility.amp.cisco.com/iroh/iroh-inspect/inspect', headers=headers, data=data,verify=True))

    def get_actions_observables(self,observable): 

        bearer_token = 'Bearer ' + self.access_token
        headers = {
            'Authorization': bearer_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        # grab the type of the observable, that is needed
        rsp= self.get_observables(observable)
        type_of_observable = rsp["apirsp"][0]['type']        

        data = json.dumps([{"value":observable, "type":type_of_observable}])
        return (self.post('https://visibility.amp.cisco.com/iroh/iroh-response/respond/observables', headers=headers, data=data,verify=True))


    def get_sightings_for_observables(self,observables):
        bearer_token = 'Bearer ' + self.access_token
        headers = {
            'Authorization': bearer_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = json.dumps(observables)
        return (self.post('https://visibility.amp.cisco.com/iroh/iroh-enrich/observe/observables', headers=headers, data=data,verify=True))
    
class ISE_ANC(CATS):
    
    def __init__(self,server,username,password,debug,logfile=""):
        CATS.__init__(self,debug,logfile)
        self.server = server
        self.username = username
        self.password = password


    def get_putdata(self,ip,mac,policy):
    
        putdata = {"OperationAdditionalData" : {"additionalData" : []} }
        if ip:
            t = {}
            t["name"] = "ipAddress"
            t["value"]= ip
            putdata["OperationAdditionalData"]["additionalData"].append(t)
        if mac:
            t = {}
            t["name"] = "macAddress"
            t["value"]= mac
            putdata["OperationAdditionalData"]["additionalData"].append(t)
        if policy:
            t = {}
            t["name"] = "policyName"
            t["value"]= policy
            putdata["OperationAdditionalData"]["additionalData"].append(t)
        return putdata


    
    def activeSessions(self):

### active sessions only available via xml :-(
        
        headers = {"ACCEPT":"application/xml"}
        url = "https://" +self.username + ":" + self.password + "@" + self.server + "/admin/API/mnt/Session/ActiveList"
        active_sessions = {}
        sessions = []
        try:
            r = requests.get(url,verify=False,headers=headers)
            status_code = r.status_code
            if  (status_code / 100) == 2:
                root = ET.fromstring(r.text)
                for s in root.iter("activeSession"):
                    tstr = {"user_name":"","calling_station_id":"","framed_ip_address":"","framed_ipv6_address":""}
                    for e in s.iter():
                        for key in tstr:
                            if e.tag == key:
                                tstr[key] = e.text

                    sessions.append(tstr)

                active_sessions.update({"sessions":sessions})
                active_sessions.update({"rtcResult":"OK"})
                return active_sessions
            else:
                errorstring = "Error in get " + str(status_code)
                return(self.error_handler(errorstring))
        except Exception as err:
            self.exception_handler(err)

    def endpoints(self,eid=""):
        headers = {"ACCEPT":"application/json","ERS-Media-Type":"identity.internaluser.1.2"}
        headers = {"ACCEPT":"application/json","Content-Type":"application/json"}

        url = "https://" + self.username + ":" + self.password + "@" + self.server + ":9060/ers/config/ancendpoint"
        if eid:
            url = url + "/" + eid

        return (self.get(url=url,headers=headers,verify=False))

    def macPolicy(self,mac=""):
        rsp = self.endpoints()
        resources = rsp["SearchResult"]["resources"]
        macs = []
        rsp = {"catsresult":"OK"}
        for item in resources:
            r1 = self.endpoints(item["id"])
            thismac = r1["ErsAncEndpoint"]["macAddress"]
            thispolicy = r1["ErsAncEndpoint"]["policyName"]
            if mac:
                mac = mac.upper()
                if mac==thismac:
                    rsp.update({"mac": thismac, "policy":thispolicy})
                    return rsp
                else:
                    pass
            else:
                macs.append({"mac": thismac, "policy":thispolicy})
        rsp.update({"macs":macs})
        return rsp
            
    def applyPolicy(self,ip,mac,policy):
        headers = {"ACCEPT":"application/json","Content-Type":"application/json"}
        mac = mac.upper()
        putdata = json.dumps(self.get_putdata(ip,mac,policy))
        url = "https://" + self.username + ":" + self.password + "@" + self.server + ":9060/ers/config/ancendpoint/apply"

        return (self.put(url=url,headers=headers,data=putdata,verify=False))

    def clearPolicy(self,ip="",mac=""):
        mac = mac.upper()
        headers = {"ACCEPT":"application/json","Content-Type":"application/json"}

        putdata = json.dumps(self.get_putdata(ip,mac,""))
        url = "https://" + self.username + ":" + self.password + "@" + self.server + ":9060/ers/config/ancendpoint/clear"
        return (self.put(url=url,headers=headers,data=putdata,verify=False))


    def listPolicies(self):
        headers = {"ACCEPT":"application/json","Content-Type":"application/json"}

        url = "https://{}:{}@{}:9060/ers/config/ancpolicy".format(self.username,self.password,self.server)
        return (self.get(url=url,headers=headers,verify=False))

class ISE_PXGRID2(CATS):
    def __init__(self,server,username,password,debug=False,logfile="",nodename=""):
        CATS.__init__(self,debug,logfile)
        self.server = server
        self.password = None
        self.nodename = nodename

        url = "https://{}:8910/pxgrid/control/AccountCreate".format(self.server)
        headers = {'Content-Type': 'application/json','Accept-Language':'application/json'}
        pdata = {
            "nodeName": self.nodename
        }
        rsp = self.post(url=url,headers=headers,data=json.dumps(pdata),verify=False)
        print(json.dumps(rsp))
        self.pxpassword = rsp["apirsp"]["password"]
        self.pxusername = rsp["apirsp"]["username"]
        print(self.pxpassword)
        print(self.pxusername)
class ISE_PXGRID(CATS):    
    
    def __init__(self,server,username,password,debug=False,logfile="",nodename="",clientcert="",clientkey="",clientkeypassword="",servercert=""):
        CATS.__init__(self,debug,logfile)
        self.server = server
        self.password = None
        self.nodename = nodename
        self.description = "my description"
        self.clientcert = clientcert        
        self.clientkey  = clientkey        
        self.clientkeypassword  = clientkeypassword
        self.servercert  = servercert
        self.log_debug("inititing pxgrid with clientcert {} clientkey {} keypasswd {} server cert {} nodename {}".format(self.clientcert,self.clientkey,self.clientkeypassword,self.servercert,self.nodename))
        try:
            service_lookup_response = self.service_lookup('com.cisco.ise.session')
            self.service = service_lookup_response['services'][0]
            while self.account_activate()['accountState'] != 'ENABLED':
                time.sleep(60)

            self.node_name = self.service['nodeName']
            self.secret = self.get_access_secret(self.node_name)['secret']
        except Exception as err:
            tmp = self.exception_refuse_init(err)
            return None
        
    def get_host_name(self):
        return self.server

    def get_node_name(self):
        self.log_debug("getting nodename: " + str(self.nodename))
        return self.nodename

    def get_password(self):
        self.log_debug("getting password: " + str(self.password))
        if self.password is not None:
            return self.password
        else:
            return ''

    def get_description(self):
        return self.description

    def get_ssl_context(self):
        self.log_debug("Creating SSL context")
        context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        if self.clientcert is not None:
            context.load_cert_chain(certfile=self.clientcert,
                                    keyfile=self.clientkey,
                                    password=self.clientkeypassword)
        context.load_verify_locations(capath=self.servercert)
        self.log_debug("Created SSL context")        
        return context


    def send_rest_request(self, url_suffix, payload):

        try:
            url = 'https://' + self.server + ':8910/pxgrid/control/' + url_suffix
            json_string = json.dumps(payload)
            self.log_debug('  url=' + url)            
            self.log_debug('  request=' + json_string)
            handler = urllib.request.HTTPSHandler(context=self.get_ssl_context())
            opener = urllib.request.build_opener(handler)
            rest_request = urllib.request.Request(url=url, data=str.encode(json_string))
            rest_request.add_header('Content-Type', 'application/json')
            rest_request.add_header('Accept', 'application/json')
#            b64 = base64.b64encode((self.get_node_name() + ':' + self.get_password()).encode()).decode()
            strtoencode = self.get_node_name() + ':' + self.get_password()
            self.log_debug("string for authz is {}".format(strtoencode))
            b64 = base64.b64encode((strtoencode).encode()).decode()
            rest_request.add_header('Authorization', 'Basic ' + b64)
            self.log_debug("here")
            rest_response = opener.open(rest_request)
            self.log_debug("here2")
            self.log_debug("rest response".format(rest_response))
            response = rest_response.read().decode()
            self.log_debug('  response=' + response)
            return json.loads(response)
#        except Exception as err:
        except Exception as err:
            if hasattr(err,'code'):
                self.log_debug("code is " + str(err.code))
            if hasattr(err,'text'):
                self.log_debug("text is " + err.text)
            if hasattr(err,'txt'):
                self.log_debug("txt is " + err.text)
            self.log_debug("error " + err.reason)
            return(self.exception_handler(err))
        
    def account_activate(self):
        payload = {}
        if self.get_description() is not None:
            payload['description'] = self.get_description()
        self.log_debug("Activating pxGrid account")
        return self.send_rest_request('AccountActivate', payload)

    def service_lookup(self, service_name):
        payload = {'name': service_name}
        self.log_debug("Looking up service")        
        return self.send_rest_request('ServiceLookup', payload)

    def get_access_secret(self, peer_node_name):
        payload = {'peerNodeName': peer_node_name}
        self.log_debug("Getting Access Secret")                
        return self.send_rest_request('AccessSecret', payload)

    def getSessions(self,ip="",mac=""):

        try:

            if ip:
                payload = '{ "ipAddress": "%s" }' % ip
                url = self.service['properties']['restBaseUrl'] + "/getSessionByIpAddress"
            else:
                if mac:
                    mac = mac.upper()
                    payload = '{ "macAddress": "%s" }' % mac
                    url = self.service['properties']['restBaseUrl'] + "/getSessionByMacAddress"
                else:
                    payload = '{}'
                    url = self.service['properties']['restBaseUrl'] + "/getSessions"

            handler = urllib.request.HTTPSHandler(context=self.get_ssl_context())
            opener = urllib.request.build_opener(handler)
            rest_request = urllib.request.Request(url=url, data=str.encode(payload))
            rest_request.add_header('Content-Type', 'application/json')
            rest_request.add_header('Accept', 'application/json')
            b64 = base64.b64encode((self.get_node_name() + ':' + self.secret).encode()).decode()
            rest_request.add_header('Authorization', 'Basic ' + b64)
            rest_response = opener.open(rest_request)
            self.log_debug('  status=' + str(rest_response.status))
            if (rest_response.status // 100) == 2:
                response = rest_response.read().decode()
                return json.loads(response)
            else:
                result = {
                    "catsresult": "Error",
                    "info": "invalid return code {}".format(str(rest_response.status)),
                }
                return result
                
        except Exception as err:
            self.exception_handler(err)


