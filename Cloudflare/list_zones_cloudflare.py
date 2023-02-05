import requests
import json
#URL
base_url = "https://api.cloudflare.com/client/v4/"
endpoint = "zones"
url = f'{base_url}{endpoint}'
#Token
token = input( "Insert Token: ")
#Parameters
parameters = {
    "per_page":500
}
#Header
header = {
    "Authorization": f'{"Bearer "}{token}',
    "Content-Type": "application/json"
}
#Request
get_request = requests.get(url, headers=header, params=parameters).json()
print (json.dumps(get_request['result_info'], indent=2, sort_keys=True))
#List zones
for zone in get_request["result"]:
    print(zone["name"])
