import requests
from requests.auth import HTTPBasicAuth
import json

################
# GLOBALS
################
PROJECT_DATA = "project_data.json"
INTEMPUS_API = "https://intempus.dk/web/v1"
INTEMPUS_API_KEY = "ec6417f864038d9b3b40fe1ea75b03a2cdf1bcd6"
USERNAME = "alexa.becerra99@gmail.com"
GET_HEADERS = {
    "Authorization": f"ApiKey {USERNAME}:{INTEMPUS_API_KEY}",
    "Accept": "application/json"
}
PUT_HEADERS = {
    "Authorization": f"ApiKey {USERNAME}:{INTEMPUS_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
if __name__ == "__main__":

    basic_auth = HTTPBasicAuth(USERNAME, INTEMPUS_API_KEY)
    headers = {
    "Authorization": f"ApiKey {USERNAME}:{INTEMPUS_API_KEY}",
    "Accept": "application/json"
    }
    timestamp = "?logical_timestamp__gt=9147597912"

    #response = requests.put(f"{INTEMPUS_API}/case/{timestamp}", headers=headers)
    response = requests.put(
                f"{INTEMPUS_API}/case/9584687/",
                headers=PUT_HEADERS,
                json={"name": "test-put"})
    print(response.json())
