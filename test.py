import requests
import json
from pprint import pprint


router = {
 "ip": "sandbox-iosxe-latest-1.cisco.com", 
 "port" : "443", 
 "Username" : "developer",
 "Password" : "C1sco12345"

}

url = "https://sandbox-iosxe-latest-1.cisco.com/restconf/data/ietf-interfaces:interfaces"



headers = {
  'Content-Type': 'application/yang-data+json',
  'Accept': 'application/yang-data+json'
}

response = requests.request("GET", url, headers=headers)

print(response.text)