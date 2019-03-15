#!/usr/bin/python3
import sys
import os
### simple class LOGGER to handle logging                                                                                           
###### initialised with prefix, e.g AM or SW or UMB                                                                                ###### initialised with logthreshold, events of severity greater or equal will be logged                                           ###### initialised with filename, if not "" then we will log to file instead of console                                             

class LOGGER:
    def __init__(self,prefix="NO PREFIX",logThreshold=0,filename=""):
        self.prefix   = prefix
        self.logThreshold = logThreshold
        self.logFilename = filename

    def log_debug(self,loglevel,message):
        if int(loglevel) <= int(self.logThreshold):
            m = self.prefix + "/" + str(loglevel) + ":" + message
            if self.logFilename:
                logfile = open(self.logFilename,"a")
                logfile.write(message)
            else:
                if not 'REQUEST_METHOD' in os.environ :
                    print(m)

    def exception_info(self,err):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
        return self.prefix + " " + estring
