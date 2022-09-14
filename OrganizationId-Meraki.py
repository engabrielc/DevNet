#Script to return the "Organization ID" from a specific "Organization" in Cisco Meraki by Enrique Gabriel

# 1. Import "requests" and "json" to make API calls and handle the data in JSON format.

import requests
import json

# 2. Define the URL based on the data that you want to get. Always use the Meraki's documentation.

url = "https://api.meraki.com/api/v1/organizations"

# 3. Write down the API Key of your account. If you don't have it, create a new one.

headers = {
  'X-Cisco-Meraki-API-Key': 'c555ba67e631fc9a95fbd4395101f0eecd363d0b'
}

# 4. Make the GET request

response = requests.get( url, headers=headers).json()

# 5. Optional sanity check: Print all the organizations to make sure that the script is working fine.

print(json.dumps(response, indent=2, sort_keys=True))

# 6. Go through every organization until you get the specific match based on the name you are looking for.

for response_org in response:
    if response_org["name"] == "Test-org":
        orgId = response_org["id"]

 # 7. Print the ID       

print (orgId)


