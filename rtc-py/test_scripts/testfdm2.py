#!/usr/bin/python3
import sys
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def fdm_login(host,username,password):

 headers = {
     "Content-Type": "application/json",
     "Accept": "application/json",
     "Authorization":"Bearer"
 }
 payload = {"grant_type": "password", "username": username, "password": password}

 request = requests.post("https://{}:{}/api/fdm/v1/fdm/token".format(host, 443),
                       json=payload, verify=False, headers=headers)
 if request.status_code != 200:
     raise Exception("Error logging in: {}".format(request.content))
 try:
     access_token = request.json()['access_token']
     return access_token
 except:
     raise


def main(arg):
    a = fdm_login(host="198.18.133.8",username="admin",password="C1sco12345")
    print(a)
    
if __name__ == "__main__":
    main(sys.argv[1:])
