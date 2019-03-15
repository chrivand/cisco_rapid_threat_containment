#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os
import rtcdb
import rtclogger


def main(argv):
    debug_level = 0
    mylogger = rtclogger.LOGGER("AMPeventDetails",debug_level,"")
    try:
        mydb = rtcdb.RTCDB()
        mydb.reset_db(False)
        result = {"rtcResult":"OK"}
    except Exception as err:
        result = { "rtcResult":"Error {}".format(mylogger.exception_info(err)) }
    print("Content-type:application/json\n\n")        
    print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])
