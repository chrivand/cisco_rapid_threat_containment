#!/usr/bin/python3

import rtcdb
import json
mydb = rtcdb.RTCDB("user","C!sco123")

mydb.reset_db()

rsp = mydb.getCredentials()
print(rsp)

creds = {
    "amp_api_key"  : "123",
    "amp_api_client_id" : "456",
    "u_orgid" : "789",
    "u_enforce_token" : "112",
    "u_investigate_token" : "345",
    "u_key" : "666",
    "u_secret" : "777",
    "tg_api_key": "888",
    "ise_server" : "ise.cisco.com",
    "ise_username" : "cisco",
    "ise_password": "cisco",
    "sw_server" : "kalle.cisco.com",
    "sw_username" : "cisco",
    "sw_password": "cisco",

    }
    
jsonstring = json.dumps(creds)

mydb.updateCredentials(jsonstring)

rsp = mydb.getCredentials()
print(rsp)
