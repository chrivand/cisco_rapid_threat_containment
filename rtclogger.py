#!/usr/bin/python3
import sys
import os
import datetime
import traceback

### simple class LOGGER to handle logging                                                                                           
###### initialised with prefix, e.g AM or SW or UMB                                                                                ###### initialised with logthreshold, events of severity greater or equal will be logged                                           ###### initialised with filename, if not "" then we will log to file instead of console                                             

SEPARATOR = "@"

class LOGGER:
    def __init__(self,prefix="NO PREFIX",logThreshold=0,filename="/tmp/rtc.log"):
        self.prefix   = prefix
        self.logThreshold = logThreshold
        self.logFilename = filename

    def log_debug(self,loglevel,message):
        if int(loglevel) <= int(self.logThreshold):
                
            m = self.prefix + SEPARATOR + str(loglevel) + SEPARATOR + str(datetime.datetime.now()) + SEPARATOR + message 
            if self.logFilename:
                logfile = open(self.logFilename,"a")
                fileinfo = os.stat(self.logFilename)
                if ( fileinfo.st_size <  100000):
                    logfile.write(m+"\n")
                logfile.close()
            else:
                if not 'REQUEST_METHOD' in os.environ :
                    print(m)

    def exception_info(self,err):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        estring = "{} {} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno,traceback.format_exc())
        return self.prefix + " " + estring

    def get_logs(self):
        logs = []
        logfile = open(self.logFilename,"r")
        for line in logfile:
            log = {}
            pars = line.split(SEPARATOR)

            try:
                log["function"] = ""
                log["function"] = pars[0]
                log["level"] = ""                        
                log["level"] = pars[1]
                log["time"] = ""                        
                log["time"] = pars[2]
                log["message"] = ""                        
                log["message"] = pars[3]            
                logs.append(log)
            except Exception as e:
                pass
    
        return(logs)
    
    def delete_logs(self):
        if os.path.exists(self.logFilename):
            os.remove(self.logFilename)
