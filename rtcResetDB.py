#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtcdb
import rtclogger
import psutil

def main(argv):
    debug_level = 0
    mylogger = rtclogger.LOGGER("resetDB",debug_level,"")

    try:
        if 'REQUEST_METHOD' in os.environ:
            post = json.loads(str(sys.stdin.read()))
            fullreset = post["fullreset"]
            debug = False
        else:
            fullreset = True
            debug = True
            
        rtcMainRunning = False
        for pid in psutil.pids():
            p = psutil.Process(pid)
            cmdline = p.cmdline()
            if ((len(cmdline) > 1) and(cmdline[1] == "/usr/lib/cgi-bin/rtcMain.py")):
                rtcMainRunning = True
        if rtcMainRunning:
            result = {"rtcResult":"Could not reset database - Stop RTC Process First"}
        else:
            mydb = rtcdb.RTCDB()
            mydb.reset_db(fullreset)
            result = {"rtcResult":"OK","fullreset":fullreset}
    except Exception as err:
        result = { "rtcResult":"Error {}".format(mylogger.exception_info(err)) }
    print("Content-type:application/json\n\n")        
    print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])
