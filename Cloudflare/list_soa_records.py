import requests

# Set up your API token
token = '         ' #Insert your token.
# Set the API endpoint, header and parameters
endpoint = 'https://api.cloudflare.com/client/v4/zones'
header = {
    "Authorization": f'{"Bearer "}{token}',
    "Content-Type": "application/json"
}
parameters = {
    "per_page":500
}
# Set the target SOA record content
target_soa_content = '         ' #Insert the SOA record you are looking for.
# Get a list of all your zones
response = requests.get(endpoint, headers=header, params=parameters)
zones = response.json()['result']
# Loop through each zone and query the SOA record
zones_with_target_soa = []
for zone in zones:
    zone_id = zone['id']
    zone_name = zone['name']
    # Set the API endpoint for the zone
    zone_endpoint = f'{endpoint}/{zone_id}/dns_records?type=SOA'
    # Query the SOA record for the zone
    response = requests.get(zone_endpoint, headers=header)
    soa_records = response.json()['result']
    # Check if the zone has the target SOA record
    for record in soa_records:
        if target_soa_content in record['content']:
            zones_with_target_soa.append(zone_name)
            break
# Print the list of zones with the target SOA record
print(f'Zones with SOA record "{target_soa_content}":')
for zone in zones_with_target_soa:
    print(zone)
