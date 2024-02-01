import requests
import json

# Token
token = "   " #Insert the token
zone_name = input("Insert Zone: ")

# URL to get all zones
url_all_zones = 'https://api.cloudflare.com/client/v4/zones'

# Parameters for getting all zones
parameters_all_zones = {
    "per_page": 500  # You can adjust per_page based on the expected number of zones
}

# Header
header = {
    "Authorization": f'Bearer {token}',
    "Content-Type": "application/json"
}

# Request to get all zones
try:
    all_zones_response = requests.get(url_all_zones, headers=header, params=parameters_all_zones).json()

    # Check if the request was successful
    if all_zones_response['success']:
        # Find the zone ID for the specified zone_name
        target_zone = next((zone for zone in all_zones_response['result'] if zone['name'] == zone_name), None)

        if target_zone:
            zone_id = target_zone['id']

            # URL to list DNS records for the specified zone
            url_list_records = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'

            # Parameters for listing DNS records
            parameters_list_records = {
                "per_page": 500  # You can adjust per_page based on the expected number of records
            }

            # Request to list DNS records
            all_records = []

            while True:
                list_records_response = requests.get(url_list_records, headers=header, params=parameters_list_records).json()

                # Check if the request was successful
                if list_records_response['success']:
                    # Append records to the list
                    all_records.extend(list_records_response['result'])

                    # Check if there are more pages
                    if 'result_info' in list_records_response and 'page' in list_records_response['result_info']:
                        current_page = list_records_response['result_info']['page']
                        total_pages = list_records_response['result_info']['total_pages']

                        if current_page < total_pages:
                            # Move to the next page
                            parameters_list_records['page'] = current_page + 1
                        else:
                            # All pages have been retrieved
                            break
                    else:
                        # No pagination information, break the loop
                        break
                else:
                    print(f"Error listing records: {list_records_response['errors'][0]['message']}")
                    break

            # Print all records
            for record in all_records:
                print(f"Record: {record['name']}, TTL: {record['ttl']}")
        else:
            print(f"Zone '{zone_name}' not found.")
    else:
        print(f"Error getting zones: {all_zones_response['errors'][0]['message']}")
except requests.exceptions.RequestException as e:
    print(f"Error making the request: {e}")
