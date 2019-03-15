#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import os


def exception_info(err):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    estring = "{} {} {} {}".format(err,exc_type, fname, exc_tb.tb_lineno)
    return estring

def main(argv):

    post = str(sys.stdin.read())
#    post = urllib.unquote(t).decode('utf8')
    creds = json.loads(post)
# todo - 
# input validation is for wimps
#
    try:
        mydb = rtcdb.RTCDB()
        mydb.updateCredentials(post)
        credstring = mydb.getCredentials()
        creds = json.loads(credstring)
        creds.update({"rtcResult":"OK"})
        ret = json.dumps(creds)
        print("Content-type:application/json\n\n")        
        print (ret)
    except Exception as err:
        print("Content-type:application/json\n\n")
        result = { "result":"Error","info":"some error {}".format(exception_info(err)) }
        print(json.dumps(result))
        return


if __name__ == "__main__":
    main(sys.argv[1:])
