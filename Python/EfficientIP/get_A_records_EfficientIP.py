import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.auth import HTTPBasicAuth

# Configuration
BASE_URL = "https://XXXX/rest"
USERNAME = "XXXX"
PASSWORD = "XXXX"
HEADERS = {"Content-Type": "application/json"}
AUTH = HTTPBasicAuth(USERNAME, PASSWORD)
VERIFY_SSL = False  # Ignore SSL warnings

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

def fetch_json(endpoint):
    """Fetch JSON from an API endpoint, handle errors, and show progress."""
    response = requests.get(f"{BASE_URL}{endpoint}", auth=AUTH, headers=HEADERS, verify=VERIFY_SSL)
    if response.status_code == 200:
        return response.json()
    return None  # No warnings, just return None

def get_dns_servers():
    """Retrieve all DNS servers."""
    return fetch_json("/dns_server_list?WHERE=dns_type='vdns'") or []

def get_dns_zones(dns_id):
    """Retrieve only forward (dnszone_is_reverse='0') and master (dnszone_type='master') zones."""
    query = f"/dns_zone_list?WHERE=dns_id={dns_id} AND dnszone_is_reverse='0' AND dnszone_type='master'"
    zones = fetch_json(query) or []
    
    # Return a list of (dnszone_id, dnszone_name) tuples
    return [(zone["dnszone_id"], zone["dnszone_name"]) for zone in zones]

def get_a_records(dns_id, dnszone_id):
    """Retrieve all A records for a given DNS zone with pagination."""
    offset = 0
    limit = 100
    records = []
    
    while True:
        endpoint = (f"/dns_rr_list?SELECT=rr_full_name,rr_type,rr_all_value"
                    f"&WHERE=dns_id={dns_id} AND dnszone_id={dnszone_id} AND rr_type='A'"
                    f"&limit={limit}&offset={offset}")
        data = fetch_json(endpoint)

        if not data:
            break  # Stop fetching if no data found

        records.extend(data)
        if len(data) < limit:
            break  # If fewer records than limit, it's the last page

        offset += limit

    return [
        {"name": record["rr_full_name"], "value": record["rr_all_value"]}
        for record in records
    ] if records else None  # Return None if no records

def process_dns_server(dns):
    """Process a single DNS server (fetch zones and records in parallel)."""
    dns_id = dns.get("dns_id")
    dns_name = dns.get("dns_name")

    if not dns_id:
        return None

    dns_zones = get_dns_zones(dns_id)  # Only forward & master zones
    zone_data = {}

    with ThreadPoolExecutor() as executor:
        future_to_zone = {executor.submit(get_a_records, dns_id, zone_id): zone_name for zone_id, zone_name in dns_zones}

        for future in as_completed(future_to_zone):
            zone_name = future_to_zone[future]
            records = future.result()
            if records:  # Only add zones with records
                zone_data[zone_name] = records

    return (dns_name, zone_data) if zone_data else None  # Skip empty servers

def main():
    print("✅ Starting DNS A record extraction. Please wait...")
    all_records = {}

    dns_servers = get_dns_servers()
    with ThreadPoolExecutor() as executor:
        future_to_dns = {executor.submit(process_dns_server, dns): dns for dns in dns_servers}

        for future in as_completed(future_to_dns):
            result = future.result()
            if result:
                dns_name, dns_data = result
                all_records[dns_name] = dns_data

    # Save to JSON file
    with open("dns_A_records.json", "w") as file:
        json.dump(all_records, file, indent=4)

    print("✅ Script completed. Output saved to dns_A_records.json")

if __name__ == "__main__":
    main()
