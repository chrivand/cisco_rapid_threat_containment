#!/usr/bin/python3                                                                                                                         
import json
import sys
import os
import ehcdb

def exception_info(err):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
    return estring

def main(argv):

    post = str(sys.stdin.read())

    try:

        dbconn = ehcdb.EHCDB()
        dbconn.updateEmailConfig(post)
        dbresult  = dbconn.getEmailConfig()
        if dbresult["result"] == "OK":
            configstring  = dbresult["configstring"]
            rsp = {"result":"OK"}
            rsp.update({"configstring": configstring})
        else:
            rsp = {"result":"DB ERROR"}


        print("Content-type:application/json\n\n")
        print(json.dumps(rsp))
        
    except Exception as err:
        print("Content-type:application/json\n\n")
        result = { "result":"Exception Error:" + exception_info(err) }
        print(json.dumps(result))

if __name__ == "__main__":
    main(sys.argv[1:])
