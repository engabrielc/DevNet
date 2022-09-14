#Script to return the "Organization ID" from Cisco Meraki by Enrique Gabriel

# 1. Import "requests" and "json" to make API calls and handle the data in JSON format.

import requests
import json

# 2. Define the base URL for the API call. Always refer to the Meraki documentation.

url = "https://api.meraki.com/api/v1/organizations"

# 3. Ask for the API Key. This is going to be the value for "X-Cisco-Meraki-API-Key" in the header.

apiKey = input("Please enter the API Key: ")

headers = {
  'X-Cisco-Meraki-API-Key': apiKey
}

# 4. Make the GET request

getRequest = requests.get( url, headers=headers).json()

# 5. Ask for the Organization name. 

orgName = input("Please enter the Organization name: ")

# 6. Go through every organization until you get the specific match based on the name you have provided. This will return the ID.

for organizations in getRequest:
    if organizations["name"] == orgName:
        orgId = organizations["id"]

 # 7. Print the Organization ID       

print (orgId)

# 8. Optional check: Print all the organizations to make sure that you have chosen the right name.
# print(json.dumps(response, indent=2, sort_keys=True))


