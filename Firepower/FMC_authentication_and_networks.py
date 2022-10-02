#Script to learn how to get the Authentication token and, an example of displaying the networks to explore this API.

import json 
import requests


url = "https://fmcrestapisandbox.cisco.com"
login_url = "/api/fmc_platform/v1/auth/generatetoken"
headers = {"Content-Type" : "application/json"}

#These variables already expired and were included them in the script for simplicity.
user = "enriquegab"
password = "WWMnafMT"

#We must post the request to the login URL.
login_response = requests.post(
     f'{url}{login_url}', auth=(user, password), verify=False)


resp_headers = login_response.headers
token = resp_headers.get("X-auth-access-token", default=None)

#We save the token in a variable called token
headers["X-auth-access-token"] = token

#This is the URL to see the available networks. Always refer to the documentation.
networks_url = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/networks"

networks_response = requests.get(
    f'{url}{networks_url}', headers=headers, verify=False).json()

#Printing the networks.
print (json.dumps(networks_response, indent=2, sort_keys=True))
