#!/usr/bin/python3

import datetime
import sys
import os
import mysql.connector
from mysql.connector import errorcode
import re
import json

configs = [ "email","testprofile"]

class EHCDB:
    def  __init__(self):
        creds = json.loads(open("ehcdb.json").read())
        self.dbusername = creds["dbusername"]                                                           
        self.dbpassword = creds["dbpassword"]
         
        try:
            self.dbconn = mysql.connector.connect(user=self.dbusername,password=self.dbpassword,host='127.0.0.1',database='EHC')
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

        for c in configs:
            try:
                self.log_debug("drop table {}".format(c))
                cursor.execute("drop table {};".format(c))
            except Exception as e:
                self.log_debug("exception drop table {}".format(c))


        for c in configs:
            try:
                cursor = self.dbconn.cursor()                
                mysqlstring = "CREATE TABLE {} (configstring VARCHAR(10000),id VARCHAR(5))".format(c)
                cursor.execute(mysqlstring)                
                jsonstring = {}
                mysqlstring = "INSERT INTO {}(configstring,id) VALUES ('{}','{}')".format(c,jsonstring,"one")
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
            result = {"result":"OK"}
            return result
        except Exception as err:
            errorstring = self.exception_info(err)            
            result = {"result":"ERROR","info":errorstring}
            return result
        
    def updateEmailConfig(self,jsonstring):
        return self.updateConfig("email",jsonstring)

    def updateTestProfileconfig(self,jsonstring):
        return self.updateConfig("testprofil",jsonstring)

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
            result.update({"result":"OK"})
            return result
        except Exception as err:
            errorstring = self.exception_info(err)            
            result = {"result":"ERROR","info":errorstring}
            return result


    def getEmailConfig(self):
        return self.getConfig("email")
    
    def getTestProfileConfig(self):
        return self.getConfig("testprofile")

