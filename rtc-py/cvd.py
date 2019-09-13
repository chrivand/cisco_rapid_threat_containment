import requests
import json

amp_client_id = "c2ef7dfd565ff6eecfce"
amp_api_key = "b9993129-f73c-4d1c-a2e0-09981aac6cb3"




def check_possibility_amp_isolation(amp_guid):
    '''
        Function that checks possibility for host isolation.
    '''

    # Format the URL to isolate endpoint
    url = "https://api.amp.cisco.com/v1/computers/{amp_guid}/isolation"
    response = requests.options(url, auth=(amp_client_id, amp_api_key))

    # Check the returned status code and print if it was sucessful or failed
    if response.status_code == 200:
        if response.headers["allow"] == "PUT":
            # endpoint can be isolated
            return("PUT")
        elif response.headers["allow"] == DELETE:
            # endpoint can be un-isolated
            return("DELETE")
    elif response.status_code == 401:
        print("Authentification failed, please check your AMP API key")
        return(False)
    else:
        print("Error occured with status code: {request.status_code}")
        return(False)



def check_status_amp_isolation(amp_guid):
    '''
        Function that checks the status of host isolation.
    '''

    # Format the URL to isolate endpoint
    url = "https://api.amp.cisco.com/v1/computers/{amp_guid}/isolation"
    response = requests.get(url, auth=(amp_client_id, amp_api_key))

    returned_data = json.loads(response.text)

    # Check the returned status code and print if it was sucessful or failed
    if response.status_code == 200:
        print(f"[200] Success")
        if returned_data["data"]["available"] == "true":
            # statusses are: not_isolated, pending_start, isolated, pending_stop
            return returned_data["data"]["status"]
    elif response.status_code == 401:
        print("Authentification failed, please check your AMP API key")
        return(False)
    else:
        print("Error occured with status code: {response.status_code}")
        return(False)



def start_amp_isolation(amp_guid):
    '''
        Function that starts host isolation.
    '''

    # Format the URL to isolate endpoint
    url = "https://api.amp.cisco.com/v1/computers/{amp_guid}/isolation"
    request = requests.put(url, auth=(amp_client_id, amp_api_key))

    # Check the returned status code and print if it was sucessful or failed
    if request.status_code == 200:
        print(f"Starting isolation for GUID: {amp_guid}")
        return(True)
    elif request.status_code == 401:
        print("Authentification failed, please check your AMP API key")
        return(False)
    elif request.status_code == 409:
        print(f"Host already isolated for GUID: {amp_guid}")
        return(False)
    else:
        print("Error occured with status code: {request.status_code}")
        return(False)




def stop_iso_amp(amp_guid):
    '''
        Function that stops host isolation.
    '''

    # Format the URL to un-isolate endpoint
    url = "https://api.amp.cisco.com/v1/computers/{amp_guid}/isolation"
    request = requests.delete(url, auth=(amp_client_id, amp_api_key))

    # Check the returned status code and print if it was sucessful or failed
    if request.status_code == 200:
        print(f"Stopping isolation for GUID: {amp_guid}")
        return(True)
    elif request.status_code == 401:
        print("Authentification failed, please check your AMP API key")
        return(False)
    elif request.status_code == 409:
        print(f"Host already un-isolated for GUID: {amp_guid}")
        return(False)
    else:
        print(f"Error occured with status code: {request.status_code}")
        return(False)



if __name__ == '__main__':
    amp_guid = "7a145ad1-c773-487a-b6d8-23a5ea62f98e"
    
    # in case of quarantine RTC
    if check_possibility_amp_isolation(amp_guid) == "PUT":
        start_amp_isolation(amp_guid)
    elif check_possibility_amp_isolation(amp_guid) == "DELETE":
        print("Endpoint already isolated")
    else:
        print("Endpoint can't be isolated, please check the connector version")

     # in case of unquarantine RTC
    if check_possibility_amp_isolation(amp_guid) == "DELETE":
        stop_amp_isolation(amp_guid)
    elif check_possibility_amp_isolation(amp_guid) == "PUT":
        print("Endpoint already un-isolated")
    else:
        print("Endpoint can't be un-isolated, please check the connector version")
