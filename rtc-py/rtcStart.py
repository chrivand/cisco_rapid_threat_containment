#!/usr/bin/python3
import json
import sys
import os
import psutil
import subprocess
import rtclogger

## define structure for simple gets (atomic structure)

def main(argv):

    debug = False    
    ### default never log,change this if needed
    try:
        post = str(sys.stdin.read())
        levels = json.loads(post)
        debug_level = 0
        mylogger = rtclogger.LOGGER("rtcStart",debug_level,"")

        if 'REQUEST_METHOD' in os.environ :
            ### this is called as CGI script and we should avoid printouts                                                              
            debug = False
        else :
            debug = True
        debug = False
        already_running = False
        for pid in psutil.pids():
            p = psutil.Process(pid)
            cmdline = p.cmdline()
            if ((len(cmdline) > 1) and(cmdline[1] == "/usr/lib/cgi-bin/rtcMain.py")):
                already_running = True
                break
        if already_running:
            rsp = {"rtcResult": "RTC Process already running"}                        
        else:
            subprocess.Popen(["/usr/lib/cgi-bin/rtcMain.py","-a",levels["amploglevel"],"-u",levels["umbloglevel"],"-s",levels["swloglevel"],"-f","/tmp/rtc.log"])
            rsp = {"rtcResult": "OK"}                                  

    except Exception as err:
        rsp = {"rtcResult": mylogger.exception_info(err)}

    print("Content-type:application/json\n\n")
    if not debug:
        print(json.dumps(rsp))
    else:
        print(json.dumps(rsp,indent=4,sort_keys=True))

if __name__ == "__main__":
    main(sys.argv[1:])
