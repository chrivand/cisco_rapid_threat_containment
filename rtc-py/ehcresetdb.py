#!/usr/bin/python3                                                                                                                         
import json
import sys
import ehcdb
import os
import rtcdb

def exception_info(err):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
    return estring

def main(argv):

#
    try:
        mydb = ehcdb.EHCDB()
        mydb.reset_db(False)
        print("have reset db")
    except Exception as err:
#        temp = exception_info(err)
        print("bajs")
        print(err)


if __name__ == "__main__":
    main(sys.argv[1:])
