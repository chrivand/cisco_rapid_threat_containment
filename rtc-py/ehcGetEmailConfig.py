#!/usr/bin/python3                                                                                                                         
import json
import sys
import ehcdb


def main(argv):
    try:
        dbconn = ehcdb.EHCDB()
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
        result = { "result":"Error","info":"some error {}".format(mylogger.exception_info(err)) }
        print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])

