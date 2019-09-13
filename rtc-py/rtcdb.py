#!/usr/bin/python3

import datetime
import sys
import os
import mysql.connector
from mysql.connector import errorcode
import re
import json
from time import gmtime,strftime
from datetime import datetime,timedelta

configs = [ "swconfig","iseconfig","ampconfig","ctrconfig","umbrellaconfig","tgconfig","rtcconfig" ]

eventtables  = [ "swevents","umbevents","ampevents"]

class RTCDB:
    def  __init__(self):
        creds = json.loads(open("rtcdb.json").read())
        self.dbusername = creds["dbusername"]                                                           
        self.dbpassword = creds["dbpassword"]
        try:
            self.dbconn = mysql.connector.connect(user=self.dbusername,password=self.dbpassword,host='127.0.0.1',database='RTC')
        except Exception as err:
            self.log_debug("error connecting to db {}".format(err))

    def exception_info(self,err):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
        return estring

    def log_debug(self,message):
        if True:
            if 'REQUEST_METHOD' in os.environ :
            # running as CGI, do not print
                pass
            else:
                print(message)
    
    def reset_db(self,fullreset):

        cursor = self.dbconn.cursor()
        if fullreset:
            for c in configs:
                try:
                    self.log_debug("drop table if exists {}".format(c))
                    cursor.execute("drop table if exists {};".format(c))
                except Exception as e:
                    self.log_debug("exception drop if exists table {}".format(c))

        try:
            self.log_debug("dropping hosts")
            cursor.execute("drop table if exists hosts;")
        except Exception as e:
            self.log_debug("exception drop table hosts")

        try:
            self.log_debug("dropping users")            
            cursor.execute("drop table if exists users;")
        except Exception as e:
            self.log_debug("exception drop table users")

        try:
            self.log_debug("dropping ips")            
            cursor.execute("drop table if exists ips;")
        except Exception as e:
            self.log_debug("exception drop table ips")

        try:
            self.log_debug("dropping hostnames")            
            cursor.execute("drop table if exists hostnames;")
        except Exception as e:
            self.log_debug("exception drop table hostnames")
            

        for e in eventtables:
            try:
                self.log_debug("drop table if exists {}".format(e))                
                cursor.execute("drop table if exists {};".format(e))
            except Exception as err:
                self.log_debug("exception drop if exists table {}".format(e))                
        try:

            if fullreset:
                for c in configs:
                    mysqlstring = "CREATE TABLE {} (configstring VARCHAR(10000),id VARCHAR(5))".format(c)
                    cursor.execute(mysqlstring)                
                    jsonstring = {}
                    mysqlstring = "INSERT INTO {}(configstring,id) VALUES ('{}','{}')".format(c,jsonstring,"one")
                    cursor.execute(mysqlstring)

                
            mysqlstring = "CREATE TABLE hosts (mac VARCHAR(20),penalty INT, rtcflag INT, updatetime DATETIME, PRIMARY KEY (mac) )"
            cursor.execute(mysqlstring)

            mysqlstring = "CREATE TABLE users (user VARCHAR(150),penalty INT, rtcflag INT, updatetime DATETIME, PRIMARY KEY (user) )"
            cursor.execute(mysqlstring)

            mysqlstring = "CREATE TABLE ips (ip VARCHAR(50),penalty INT, rtcflag INT, updatetime DATETIME, PRIMARY KEY (ip) )"
            cursor.execute(mysqlstring)
            
            mysqlstring = "CREATE TABLE hostnames (hostname VARCHAR(150),penalty INT, rtcflag INT, updatetime DATETIME, PRIMARY KEY (hostname) )"
            cursor.execute(mysqlstring)

            for e in eventtables:
                mysqlstring = "CREATE TABLE {} (mac VARCHAR(20),observable VARCHAR(100),user VARCHAR(150),hostname VARCHAR(150),ip VARCHAR(50),penalty INT,eventstring VARCHAR(2000), updatetime DATETIME, eventid INT AUTO_INCREMENT, PRIMARY KEY (eventid))".format(e)
                cursor.execute(mysqlstring)
                
            cursor.close()
        except Exception as err:
            errorstring = self.exception_info(err)
            self.log_debug(errorstring)
            
    def updateConfig(self,tablename,jsonstring):
        try:
            cursor = self.dbconn.cursor()
            mysqlstring = "update {} set configstring='{}' where id='{}'".format(tablename,jsonstring,"one")
#            self.log_debug(mysqlstring)
            cursor.execute(mysqlstring)
            self.dbconn.commit()
            cursor.close()
            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            errorstring = self.exception_info(err)            
            result = {"rtcResult":"ERROR","info":errorstring}
            return result
        
    def updateSWconfig(self,jsonstring):
        return self.updateConfig("swconfig",jsonstring)

    def updateISEconfig(self,jsonstring):
        return self.updateConfig("iseconfig",jsonstring)

    def updateAMPconfig(self,jsonstring):
        return self.updateConfig("ampconfig",jsonstring)

    def updateCTRconfig(self,jsonstring):
        return self.updateConfig("ctrconfig",jsonstring)

    def updateUMBRELLAconfig(self,jsonstring):
        return self.updateConfig("umbrellaconfig",jsonstring)

    def updateRTCconfig(self,jsonstring):
        return self.updateConfig("rtcconfig",jsonstring)
    
    
    def getConfig(self,table):
        try:
            cursor = self.dbconn.cursor()
            mysqlstring = "select configstring from {} where id = 'one'".format(table)
 #           self.log_debug(mysqlstring)
            cursor.execute(mysqlstring)
            sqlresult = cursor.fetchone()
            configstring = sqlresult[0]
            result = {}
            result.update({"configstring":configstring})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            errorstring = self.exception_info(err)            
            result = {"rtcResult":"ERROR","info":errorstring}
            return result


    def getSWconfig(self):
        return self.getConfig("swconfig")
    
    def getISEconfig(self):
        return self.getConfig("iseconfig")

    def getAMPconfig(self):
        return self.getConfig("ampconfig")

    def getCTRconfig(self):
        return self.getConfig("ctrconfig")
    
    def getUMBRELLAconfig(self):
        return self.getConfig("umbrellaconfig")

    def getRTCconfig(self):
        return self.getConfig("rtcconfig")
    
    def insertEvent(self,table,mac,user,ip,hostname,observable,penalty,eventstring):
        try:
            if mac:
                mac = mac.upper()
            cursor = self.dbconn.cursor()
#            self.log_debug("inside rtcdb eventstring:" + eventstring)
            eventtime ="2018-09-20 18:00:00"
            eventtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
#            self.log_debug("eventtime {}".format(eventtime))
            mysqlstring = "INSERT INTO {}(mac,user,ip,hostname,observable,penalty,eventstring,updatetime) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')".format(table,mac,user,ip,hostname,observable,penalty,eventstring,eventtime)
            cursor.execute(mysqlstring)
            self.dbconn.commit()            
            result = {"rtcResult": "OK" }
            return result
        except Exception as err:
            self.log_debug(self.exception_info(err))
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result

    def insertAMPevent(self,mac,penalty,observable,eventstring,user="",ip="",hostname=""):
        return self.insertEvent("ampevents",mac,user,ip,hostname,observable,penalty,eventstring)

    def insertUMBevent(self,mac,penalty,observable,eventstring,user="",ip="",hostname=""):
        return self.insertEvent("umbevents",mac,user,ip,hostname,observable,penalty,eventstring)

    def insertSWevent(self,mac,penalty,observable,eventstring,user="",ip="",hostname=""):
        return self.insertEvent("swevents",mac,user,ip,hostname,observable,penalty,eventstring)

    def getEvents(self,table,mac,user,ip,hostname,observable,fromdate=""):

        try:
            mysqlstring = "SELECT mac,user,ip,hostname,observable,eventstring,updatetime,penalty,eventid FROM {} ".format(table)
            mysqlwhere = ""
            if mac:
                mac = mac.upper()
                mysqlwhere = " where mac='{}'".format(mac)
            if user:
                if not mysqlwhere:
                    mysqlwhere = " where user='{}'".format(user)
                else:
                    mysqlwhere = mysqlwhere + " and user='{}'".format(user)
            if ip:
                if not mysqlwhere:
                    mysqlwhere = " where ip='{}'".format(ip)
                else:
                    mysqlwhere = mysqlwhere + " and ip='{}'".format(ip)
            if hostname:
                if not mysqlwhere:
                    mysqlwhere = " where hostname='{}'".format(hostname)
                else:
                    mysqlwhere = mysqlwhere + " and hostname='{}'".format(hostname)                
            if observable:
                if not mysqlwhere:
                    mysqlwhere = " where observable='{}'".format(observable)
                else:
                    mysqlwhere = mysqlwhere + "  and observable='{}'".format(observable)
            if fromdate:
                if not mysqlwhere:
                    mysqlwhere = " where updatetime >'{}'".format(fromdate)
                else:
                    mysqlwhere =  mysqlwhere + " and updatetime > '{}'".format(fromdate)

            mysqlstring = mysqlstring + mysqlwhere
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            row = cursor.fetchone()
            events = []
            while row is not None:
                event = {}
                event["mac"] = str(row[0])
                event["user"] = str(row[1])
                event["ip"] = str(row[2])
                event["hostname"] = str(row[3])                                
                event["observable"] = str(row[4])                
                event["eventstring"] = json.loads(row[5])
                event["updatetime"]   = str(row[6])
                event["penalty"]   = str(row[7])
                event["eventid"]   = str(row[8])                                
                events.append(event.copy())
                row = cursor.fetchone()

            result = {}
            result.update({"events":events})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result

    def getEventById(self,table,eventid):

        try:
            mysqlstring = "SELECT mac,user,ip,hostname,observable,eventstring,updatetime,penalty FROM {} ".format(table)
            mysqlwhere = " where eventid = '{}'".format(eventid)
            mysqlstring = mysqlstring + mysqlwhere
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            row = cursor.fetchone()
            events = []
            while row is not None:
                event = {}
                event["mac"] = str(row[0])
                event["user"] = str(row[1])
                event["ip"] = str(row[2])
                event["hostname"] = str(row[3])                                
                event["observable"] = str(row[4])                
                event["eventstring"] = json.loads(row[5])
                event["updatetime"]   = str(row[6])
                event["penalty"]   = str(row[7])                
                events.append(event.copy())
                row = cursor.fetchone()
            result = {}
            result.update({"events":events})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result
        
    def getAMPevents(self,mac="",fromdate = "",user="",ip="",hostname="",observable=""):
        return self.getEvents("ampevents",mac,user,ip,hostname,observable,fromdate)

    def getUMBevents(self,mac="",rtcid=0,fromdate = "",user="",ip="",hostname="",observable=""):
        return self.getEvents("umbevents",mac,user,ip,hostname,observable,fromdate)

    def getSWevents(self,mac="",rtcid=0,fromdate = "",user="",ip="",hostname="",observable=""):
        return self.getEvents("swevents",mac,user,ip,hostname,observable,fromdate)

    def getAMPeventById(self,eventid):
        return self.getEventById("ampevents",eventid)

    def getUMBeventById(self,eventid):
        return self.getEventById("umbevents",eventid)
    
    def getSWeventById(self,eventid):
        return self.getEventById("swevents",eventid)
    
            
    def updateHost(self,mac,penalty):
        try:

            if mac:
                mac = mac.upper()
                
            eventtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            cursor = self.dbconn.cursor()            
            rsp = self.getHosts(mac)
            hosts = rsp["hosts"]
            if hosts:
                old_penalty = hosts[0]["penalty"]
                penalty = int(penalty) + int(old_penalty)
                mysqlstring = "UPDATE hosts SET penalty=%s,updatetime=%s WHERE mac=%s"
                val = (penalty,eventtime,mac)
                cursor.execute(mysqlstring,val)                
            else:
                mysqlstring = "INSERT INTO hosts(mac,penalty,updatetime) VALUES ('{}',{},'{}')".format(mac,penalty,eventtime)                
                cursor.execute(mysqlstring)


            self.dbconn.commit()            
            result = {"rtcResult": "OK" }
            return result
        except Exception as err:
            self.log_debug(self.exception_info(err))
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result


    def getHosts(self,mac=""):

        try:
            if mac:
                mac = mac.upper()
                mysqlstring = "SELECT mac,penalty FROM hosts where mac =  '{}'".format(mac)
            else:
                mysqlstring = "SELECT mac,penalty FROM hosts ORDER BY penalty DESC"
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            row = cursor.fetchone()
            hosts = []
            while row is not None:
                host = {}
                host["mac"] = row[0]
                host["penalty"] = row[1]                
                hosts.append(host.copy())
                row = cursor.fetchone()
            result = {}
            result.update({"hosts":hosts})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result

    def updateUser(self,user,penalty):
        try:

            eventtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            rsp = self.getUsers(user)
            cursor = self.dbconn.cursor()            
            users = rsp["users"]
            if users:
                old_penalty = users[0]["penalty"]
                new_penalty = int(penalty) + int(old_penalty)
                mysqlstring = "UPDATE users SET penalty=%s,updatetime=%s WHERE user=%s"
                val = (new_penalty,eventtime,user)
                cursor.execute(mysqlstring,val)                
            else:
                mysqlstring = "INSERT INTO users(user,penalty,updatetime) VALUES ('{}',{},'{}')".format(user,penalty,eventtime)                
                cursor.execute(mysqlstring)


            self.dbconn.commit()            
            result = {"rtcResult": "OK" }
            return result
        except Exception as err:
            self.log_debug(self.exception_info(err))
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result


    def getUsers(self,user=""):

        try:
            if user:
                mysqlstring = "SELECT user,penalty FROM users where user =  '{}'".format(user)
            else:
                mysqlstring = "SELECT user,penalty FROM users ORDER BY penalty DESC"
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            row = cursor.fetchone()
            users = []
            while row is not None:
                user = {}
                user["user"] = row[0]
                user["penalty"] = row[1]                
                users.append(user.copy())
                row = cursor.fetchone()
            result = {}
            result.update({"users":users})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result



    def updateIP(self,ip,penalty):
        try:

            eventtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            rsp = self.getIPs(ip)
            cursor = self.dbconn.cursor()            
            ips = rsp["ips"]
            if ips:
                old_penalty = ips[0]["penalty"]
                new_penalty = int(penalty) + int(old_penalty)
                mysqlstring = "UPDATE ips SET penalty=%s,updatetime=%s WHERE ip=%s"
                val = (new_penalty,eventtime,ip)
                cursor.execute(mysqlstring,val)                
            else:
                mysqlstring = "INSERT INTO ips(ip,penalty,updatetime) VALUES ('{}',{},'{}')".format(ip,penalty,eventtime)                
                cursor.execute(mysqlstring)


            self.dbconn.commit()            
            result = {"rtcResult": "OK" }
            return result
        except Exception as err:
            self.log_debug(self.exception_info(err))
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result


    def getIPs(self,ip=""):

        try:
            if ip:
                mysqlstring = "SELECT ip,penalty FROM ips where ip =  '{}'".format(ip)
            else:
                mysqlstring = "SELECT ip,penalty FROM ips ORDER BY penalty DESC"
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            row = cursor.fetchone()
            ips = []
            while row is not None:
                ip = {}
                ip["ip"] = row[0]
                ip["penalty"] = row[1]                
                ips.append(ip.copy())
                row = cursor.fetchone()
            result = {}
            result.update({"ips":ips})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result


    def updateHostname(self,hostname,penalty):
        try:

            eventtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            rsp = self.getHostnames(hostname)
            cursor = self.dbconn.cursor()            
            hostnames = rsp["hostnames"]
            if hostnames:
                old_penalty = hostnames[0]["penalty"]
                new_penalty = int(penalty) + int(old_penalty)
                mysqlstring = "UPDATE hostnames SET penalty=%s,updatetime=%s WHERE hostname=%s"
                val = (new_penalty,eventtime,hostname)
                cursor.execute(mysqlstring,val)                
            else:
                mysqlstring = "INSERT INTO hostnames(hostname,penalty,updatetime) VALUES ('{}',{},'{}')".format(hostname,penalty,eventtime)                
                cursor.execute(mysqlstring)


            self.dbconn.commit()            
            result = {"rtcResult": "OK" }
            return result
        except Exception as err:
            self.log_debug(self.exception_info(err))
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result


    def getHostnames(self,hostname=""):

        try:
            if hostname:
                mysqlstring = "SELECT hostname,penalty FROM hostnames where hostname =  '{}'".format(hostname)
            else:
                mysqlstring = "SELECT hostname,penalty FROM hostnames ORDER BY penalty DESC"
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            row = cursor.fetchone()
            hostnames = []
            while row is not None:
                hostname = {}
                hostname["hostname"] = row[0]
                hostname["penalty"] = row[1]                
                hostnames.append(hostname.copy())
                row = cursor.fetchone()
            result = {}
            result.update({"hostnames":hostnames})
            result.update({"rtcResult":"OK"})
            return result
        except Exception as err:
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result


    def deleteEvents(self,table,mac="",user="",ip="",hostname=""):

        try:
            mysqlstring = "DELETE FROM {} ".format(table)
            mysqlwhere = ""
            if mac:
                mac = mac.upper()
                mysqlwhere = " where mac='{}'".format(mac)
            if user:
                if not mysqlwhere:
                    mysqlwhere = " where user='{}'".format(user)
                else:
                    mysqlwhere = mysqlwhere + " and user='{}'".format(user)
            if ip:
                if not mysqlwhere:
                    mysqlwhere = " where ip='{}'".format(ip)
                else:
                    mysqlwhere = mysqlwhere + " and ip='{}'".format(ip)
            if hostname:
                if not mysqlwhere:
                    mysqlwhere = " where hostname='{}'".format(hostname)
                else:
                    mysqlwhere = mysqlwhere + " and hostname='{}'".format(hostname)

            mysqlstring = mysqlstring + mysqlwhere
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            self.dbconn.commit()                        
            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result


    def deleteIP(self,ip):

        try:
            mysqlstring = "DELETE FROM {} WHERE IP='{}'" .format("ips",ip)
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            self.dbconn.commit()
            self.deleteEvents("ampevents",ip=ip)
            self.deleteEvents("swevents",ip=ip)
            self.deleteEvents("umbevents",ip=ip)

            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            print(self.exception_info(err))
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result


    def deleteHostname(self,hostname):

        try:
            mysqlstring = "DELETE FROM {} WHERE HOSTNAME='{}'" .format("hostnames",hostname)
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            self.dbconn.commit()
            self.deleteEvents("ampevents",hostname=hostname)
            self.deleteEvents("swevents",hostname=hostname)
            self.deleteEvents("umbevents",hostname=hostname)

            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            print(self.exception_info(err))
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result

    def deleteHost(self,host):

        try:
            mysqlstring = "DELETE FROM {} WHERE HOST='{}'" .format("host",host)
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            self.dbconn.commit()
            self.deleteEvents("ampevents",host=host)
            self.deleteEvents("swevents",host=host)
            self.deleteEvents("umbevents",host=host)

            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            print(self.exception_info(err))
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result

    def deleteUser(self,username):

        try:
            mysqlstring = "DELETE FROM {} WHERE USER='{}'" .format("users",username)
            cursor = self.dbconn.cursor()
            cursor.execute(mysqlstring)
            self.dbconn.commit()
            self.deleteEvents("ampevents",username=username)
            self.deleteEvents("swevents",username=username)
            self.deleteEvents("umbevents",username=username)

            result = {"rtcResult":"OK"}
            return result
        except Exception as err:
            print(self.exception_info(err))
            result = {"rtcResult": "Error","info":self.exception_info(err) }
            return result
        
        
