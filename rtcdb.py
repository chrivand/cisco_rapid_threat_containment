#!/usr/bin/python3

import datetime
import sys
import os
import pymongo
import re
import json
from time import gmtime,strftime
from datetime import datetime,timedelta
import rtclogger

configs = [ "swconfig","iseconfig","ampconfig","ctrconfig","umbrellaconfig","tgconfig","rtcconfig","adconfig" ]

objects = ["hosts","users","ips","hostnames"]

eventtables  = [ "swevents","umbevents","ampevents"]

class RTCDB:
    def  __init__(self):
        creds = json.loads(open("/usr/lib/cgi-bin/rtcdb.json").read())
        self.dbusername = creds["dbusername"]                                                           
        self.dbpassword = creds["dbpassword"]
        if 'REQUEST_METHOD' in os.environ:
            filename = "/tmp/rtcdb.log"
        else:
            filename = "/tmp/rtcdb2.log"
        self.logger = rtclogger.LOGGER(prefix="RTCDB",filename=filename)
        self.dbconn = None

    def exception_info(self,err):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
        return estring
        
    def connect(self):
                
        try:
            myclient = pymongo.MongoClient("mongodb://db:27017/")
            self.mydb = myclient["RTC"]
                
        except Exception as err:
            self.log_debug("error connecting to db {}".format(self.exception_info(err)))
    

    def log_debug(self,message):
        if True:
            if 'REQUEST_METHOD' in os.environ :
            # running as CGI, do not print
                self.logger.log_debug(0,message)
            else:
                print(message)
    
    def reset_db(self,fullreset):

        self.connect()
        if fullreset:
            for c in configs:
                try:
                    self.log_debug("drop collection if exists {}".format(c))
                    mycol = self.mydb[c]
                    mycol.drop()
                except Exception as e:
                    self.log_debug("exception collection if exists {}".format(c))

        for o in objects:
            try:
                self.log_debug("dropping {}".format(o))
                mycol = self.mydb[o]
                mycol.drop()
            except Exception as e:
                self.log_debug("exception drop collection {}".format(o))


        for e in eventtables:
            try:
                self.log_debug("drop table if exists {}".format(e))                
                mycol = self.mydb[e]
                mycol.drop()
            except Exception as err:
                self.log_debug("exception drop if exists table {}".format(e))                

        try:

            if fullreset:
                for c in configs:
                    mycol = self.mydb[c]
                    mydict = {"name":c,"config":{}}
                    mycol.insert_one(mydict)

            for o in objects:
                pass
            for e in eventtables:
                pass

        except Exception as err:
            errorstring = self.exception_info(err)
            self.log_debug(errorstring)
            


    def restoreConfig(self,config):
        try:
            self.log_debug("restoring config, config is  " )
            self.connect()
            for c in config:
                table = c["table"]                
                self.log_debug("restoring config " + json.dumps(c) )                                            
                config = c["configstring"]
                mycol = self.mydb[table]
                mycol.drop()
                self.log_debug("dropped config " + table )                                                            
                mydict = {"table":table,"config":config}
                mycol.insert_one(mydict)
                self.log_debug("restored config " + table + " " + json.dumps(c))                            
            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            errorstring = self.exception_info(err)
            self.log_debug(errorstring)            
            result = {"rtcResult":"ERROR","info":errorstring}
            return result
                
    def updateConfig(self,table,jsonstring):
        try:
            config = json.loads(jsonstring)
            self.connect()
            mycol = self.mydb[table]
            mycol.drop()
            mydict = {"table":table,"config":config}
            mycol.insert_one(mydict)
            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            errorstring = self.exception_info(err)            
            result = {"rtcResult":"ERROR","info":errorstring }
#            raise err
            return result
        

    def updateRTCconfig(self,jsonstring):
        return self.updateConfig("rtcconfig",jsonstring)
    
    
    def getConfig(self,table):
        try:

            self.connect()
            mycol = self.mydb[table]
            mydict = mycol.find_one()
            result = {}
            configstring = json.dumps(mydict["config"])
            result.update({"configstring":configstring})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            self.logger.log_debug(0,self.exception_info(err))
            raise


    def getXconfig(self,table):

        if table:
            ## self.connect called from getconfig
            return self.getConfig(table)
        else:
            self.connect()                    
            ''' get all configs '''
            allconfigs = []
            for config in configs:
                try:
                    mycol = self.mydb[config]
                    mydict = mycol.find_one()
                    thisconfig = {}
                    thisconfig = { "table": config,"configstring": mydict["config"]}
                    allconfigs.append(thisconfig)

                except Exception as err:
                    errorstring = self.exception_info(err)            
                    result = {"rtcResult":"ERROR","info":errorstring}
                    return result

            result = {"rtcResult":"OK"}    
            result.update({"configstring":allconfigs})                    
            return result
        

    def updateXconfig(self,table,jsonstring):        
        return self.updateConfig(table,jsonstring)
    
    def insertEvent(self,table,mac,user,ip,hostname,observable,penalty,eventstring):
        try:
            self.connect()
            if mac:
                mac = mac.upper()
            eventinfo = json.loads(eventstring)
            eventtime ="2018-09-20 18:00:00"
            eventtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            mycol = self.mydb[table]
            mydict = { "mac": mac,
                       "ip": ip,
                       "user":user,
                       "hostname":hostname,
                       "observable":observable,
                       "penalty": penalty,
                       "eventstring": eventinfo,
                       "updatetime": eventtime
                       }
            mycol.insert_one(mydict)
            result = {"rtcResult": "OK" }
            return result
        except Exception as err:
            self.log_debug(self.exception_info(err))
            raise

    def insertAMPevent(self,mac,penalty,observable,eventstring,user="",ip="",hostname=""):
        return self.insertEvent("ampevents",mac,user,ip,hostname,observable,penalty,eventstring)

    def insertUMBevent(self,mac,penalty,observable,eventstring,user="",ip="",hostname=""):
        return self.insertEvent("umbevents",mac,user,ip,hostname,observable,penalty,eventstring)

    def insertSWevent(self,mac,penalty,observable,eventstring,user="",ip="",hostname=""):
        return self.insertEvent("swevents",mac,user,ip,hostname,observable,penalty,eventstring)

    def getEvents(self,table,mac,user,ip,hostname,observable,fromdate=""):

        try:
            self.connect()
            mycol = self.mydb[table]

            search = {}
            if mac:
                mac = mac.upper()
                search.update({"mac":mac})
            if user:
                search.update({"user":user})
            if ip:
                search.update({"ip":ip})
            if hostname:
                search.update({"hostname":hostname})

            events = []
            results = mycol.find(search)
            for r in results:
                # t = {"event_id",r["_id"]}
                r.pop("_id")
                # r.update(t)
                events.append(r)
            result = {}
            result.update({"events":events})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            self.log_debug(0,self.exception_info(err) + " ")
            raise

    def getAMPevents(self,mac="",fromdate = "",user="",ip="",hostname="",observable=""):
        rsp = self.getEvents("ampevents",mac,user,ip,hostname,observable,fromdate)
        return rsp
    def getUMBevents(self,mac="",rtcid=0,fromdate = "",user="",ip="",hostname="",observable=""):
        return self.getEvents("umbevents",mac,user,ip,hostname,observable,fromdate)

    def getSWevents(self,mac="",rtcid=0,fromdate = "",user="",ip="",hostname="",observable=""):
        return self.getEvents("swevents",mac,user,ip,hostname,observable,fromdate)

    def getEventById(self,table,eventid):
        try:
            self.connect()
            mycol = self.mydb[table]

            search = {"_id": eventid}
            events = []
            results = mycol.find(search)
            for r in results:
                r.pop("_id")
                events.append(r)
            result = {}
            result.update({"events":events})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            self.log_debug(0,self.exception_info(err) + " ")
            raise
        
    def getAMPeventById(self,eventid):
        return self.getEventById("ampevents",eventid)

    def getUMBeventById(self,eventid):
        return self.getEventById("umbevents",eventid)
    
    def getSWeventById(self,eventid):
        return self.getEventById("swevents",eventid)
    
            
    def updateObj(self,table,keyitem,keyval,penalty):
        try:

            if table == "hosts":
                # convert mac to upper case
                keyval = keyval.upper()

            eventtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            myquery = {keyitem:keyval}
            self.connect()
            mycol = self.mydb[table]
            result = mycol.find_one(myquery)
            if result:
                old_penalty = result["penalty"]
                penalty = int(penalty) + int(old_penalty)
                mycol.delete_one(myquery)

            newitem = {
                keyitem: keyval,
                "penalty": penalty,
                "eventtime": eventtime
                }
            mycol.insert(newitem)
            result = {"rtcResult": "OK" }
            return result
        except Exception as err:
            self.log_debug(0,self.exception_info(err))
            raise

    def getObjs(self,table,keyitem,keyval=""):

        try:
            self.connect()
            mycol = self.mydb[table]
            if keyval:
                myquery = {keyitem:keyval}
                results = mycol.find(myquery)
            else:
                results = mycol.find()
            items = []
            for r in results:
                r.pop("_id")
                items.append(r)
            result = {}
            result.update({"items":items})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            self.logger.log_debug(0,self.exception_info(err))            
            raise
        
    def updateHost(self,mac,penalty):
        return(self.updateObj("hosts","mac",mac,penalty))
        
    def getHosts(self,mac=""):
        return(self.getObjs("hosts","mac",mac))

    def updateUser(self,user,penalty):
        return(self.updateObj("users","user",user,penalty))

    def getUsers(self,user=""):
        return(self.getObjs("users","user",user))

    def updateIP(self,ip,penalty):
        return(self.updateObj("ips","ip",ip,penalty))

    def getIPs(self,ip=""):
        return(self.getObjs("ips","ip",ip))

    def updateHostname(self,hostname,penalty):
        return(self.updateObj("hostnames","hostname",hostname,penalty))

    def getHostnames(self,hostname=""):
        return(self.getObjs("hostnames","hostname",hostname))

    def deleteEvents(self,table,mac="",user="",ip="",hostname=""):

        try:        
            if mac:
                mac = mac.upper()

            self.connect()
            mycol = self.mydb[table]
            myquery = {}
            ''' should we delete all the evants even if only one match? '''
        
            if mac:
                myquery.update({"mac": mac})
            if ip:
                myquery.update({"ip": ip})
            if user:
                myquery.update({"user": user})
            if hostname:
                myquery.update({"hostname": hostname})
            '''
            myquery = {"mac": mac,
                       "ip": ip,
                       "user": user,
                       "hostname": hostname}
            '''
            self.log_debug("Deleting many " + str(myquery))
            mycol.delete_many(myquery)
            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            raise

    def deleteObj(self,table,keyitem,keyvalue):

        try:
            self.connect()
            mycol = self.mydb[table]
            myquery = {keyitem:keyvalue}
            mycol.delete_one(myquery)
            if table == "hosts":
                self.deleteEvents("ampevents",mac=keyvalue)
                self.deleteEvents("swevents",mac=keyvalue)
                self.deleteEvents("umbevents",mac=keyvalue)
            if table == "hostsnames":
                self.deleteEvents("ampevents",hostname=keyvalue)
                self.deleteEvents("swevents",hostname=keyvalue)
                self.deleteEvents("umbevents",hostname=keyvalue)
            if table == "ips":
                self.deleteEvents("ampevents",ip=keyvalue)
                self.deleteEvents("swevents",ip=keyvalue)
                self.deleteEvents("umbevents",ip=keyvalue)
            if table == "users":
                self.deleteEvents("ampevents",user=keyvalue)
                self.deleteEvents("swevents",user=keyvalue)
                self.deleteEvents("umbevents",user=keyvalue)

                
            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            self.log_debug(self.exception_info(err))
            raise

    def deleteIP(self,ip):
        self.deleteObj("ips","ip",ip)

    def deleteHostname(self,hostname):
        self.deleteObj("hostnames","hostname",hostname)

    def deleteHost(self,host):
        self.deleteObj("hosts","mac",host)

    def deleteUser(self,username):
        self.deleteObj("users","user",username)
        
