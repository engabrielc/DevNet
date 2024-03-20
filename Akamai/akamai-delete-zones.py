import requests  # Importing requests library for making HTTP requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc  # Importing Akamai EdgeGridAuth for authentication
from urllib.parse import urljoin  # Importing urljoin function for joining base URL and path
import urllib3  # Importing urllib3 to disable insecure request warnings

# Disabling insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Reading Akamai EdgeRC configuration file
edgerc = EdgeRc('~/.edgerc')
section = 'default'

# Getting base URL from EdgeRC configuration
baseurl = 'https://%s' % edgerc.get(section, 'host')

# Setting the path for API endpoint
path='/config-dns/v2/zones/delete-requests'

# Setting headers for the request
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

# Read the list of zones from the text file
with open('zones_to_delete.txt', 'r') as file:
    zones_to_delete = [line.strip() for line in file]

# Create payload with zones to be deleted
payload = { "zones": zones_to_delete }

# Creating a session object for making HTTP requests
s = requests.Session()

# Authenticating the session using EdgeGridAuth
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

# Making a POST request to the API endpoint with the provided payload and headers
result = s.post(urljoin(baseurl, path), json=payload, headers=headers, verify=False)

# Printing the response text
print(result.text)
