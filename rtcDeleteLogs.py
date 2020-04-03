#!/usr/bin/python3
import json
import sys
import os
import rtclogger


def main(argv):

    try:

        debug = True
        if 'REQUEST_METHOD' in os.environ :
            debug = False
        logger = rtclogger.LOGGER(filename="/tmp/rtc.log")
        logs = logger.delete_logs()
        rsp = {"rtcResult": "OK"}

    except Exception as err:
        rsp = {"rtcResult": logger.exception_info(err)}

    print("Content-type:application/json\n\n")
    if not debug:
        print(json.dumps(rsp))
    else:
        print(json.dumps(rsp,indent=4,sort_keys=True))

if __name__ == "__main__":
    main(sys.argv[1:])
