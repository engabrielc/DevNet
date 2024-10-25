import concurrent.futures
import requests
import pandas as pd
import getpass  # Secure password input
from typing import Tuple

# Disable SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings()

# Function to authenticate and get session token and CSRF token
def authenticate(controller_url: str, username: str, password: str) -> Tuple[str, str, requests.Session]:
    login_url = f'{controller_url}/login'
    session = requests.Session()  # Reuse a session for better performance
    try:
        response = session.post(login_url, data={'username': username, 'password': password}, verify=False)
        response.raise_for_status()  # Ensure login is successful
        cookies = response.cookies.get_dict()
        sessionid = cookies.get('sessionid')
        csrftoken = cookies.get('csrftoken')

        if sessionid and csrftoken:
            print("Authentication successful!")
            return sessionid, csrftoken, session
        else:
            print("Failed to retrieve session or CSRF token.")
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error during authentication: {e}")
        return None, None, None

# Function to get the UUID and status of a virtual service by VIP name
def get_virtual_service_uuid_and_status(controller_url: str, session: requests.Session, sessionid: str, csrftoken: str, tenant_name: str, vip_name: str) -> Tuple[str, str, bool]:
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json;charset=UTF-8',
        'cookie': f'sessionid={sessionid}; csrftoken={csrftoken}',
        'x-avi-tenant': tenant_name,
        'x-avi-useragent': 'UI',
        'x-csrftoken': csrftoken,
        'x-avi-version': '22.1.6'
    }

    vs_url = f'{controller_url}/api/virtualservice?include_name&name={vip_name}'
    try:
        response = session.get(vs_url, headers=headers, verify=False)
        response.raise_for_status()
        virtual_services = response.json().get('results', [])
        if virtual_services:
            vs_uuid = virtual_services[0]['uuid']
            vs_name = virtual_services[0]['name']
            vs_enabled = virtual_services[0]['enabled']  # Get the enabled status
            return vs_uuid, vs_name, vs_enabled
        else:
            print(f"Virtual Service with name '{vip_name}' not found in tenant '{tenant_name}'.")
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving UUID for Virtual Service '{vip_name}' in tenant '{tenant_name}': {e}")
        return None, None, None

# Function to modify the status of a virtual service
def modify_virtual_service(controller_url: str, session: requests.Session, sessionid: str, csrftoken: str, tenant_name: str, vs_uuid: str, vs_name: str, enable: bool) -> None:
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json;charset=UTF-8',
        'cookie': f'sessionid={sessionid}; csrftoken={csrftoken}',
        'x-avi-tenant': tenant_name,
        'x-avi-useragent': 'UI',
        'x-csrftoken': csrftoken,
        'x-avi-version': '22.1.6'
    }

    vs_url = f'{controller_url}/api/virtualservice/{vs_uuid}?include_name'
    payload = {"replace": {"enabled": enable}}

    try:
        response = session.patch(vs_url, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        action = "enabled" if enable else "disabled"
        print(f"Virtual Service '{vs_name}' {action} successfully for tenant '{tenant_name}'.")
    except requests.exceptions.RequestException as e:
        action = "enable" if enable else "disable"
        print(f"Failed to {action} Virtual Service '{vs_name}' for tenant '{tenant_name}'. Error: {e}")

# Function to handle VIPs from CSV, check status, and disable/enable as needed
def manage_vips_from_csv():
    # Prompt for the controller IP
    controller_ip = input("Enter the AVI Controller IP (e.g., 10.0.0.200): ")
    controller_url = f'https://{controller_ip}'

    # Prompt for username and password
    username = input("Enter your AVI username: ")
    password = getpass.getpass("Enter your AVI password: ")

    # Ask whether the user wants to disable or enable (rollback)
    action = input("Do you want to disable the VIPs or enable them? (type 'disable' or 'enable'): ").strip().lower()
    enable = action == 'enable'

    # Authenticate and get session token and CSRF token
    sessionid, csrftoken, session = authenticate(controller_url, username, password)
    if not sessionid or not csrftoken:
        print("Login failed.")
        return

    # Load CSV data with tenants and VIP names
    csv_file_path = 'virtual_services.csv'  # Update this path if needed
    df = pd.read_csv(csv_file_path)

    # List to keep track of already disabled VIPs
    already_disabled_vips = []

    # First pass: Check which VIPs are already disabled concurrently
    def check_vip_status(row):
        tenant = row['Tenant']
        vip_name = row['VIP Name']
        vs_uuid, vs_name, vs_enabled = get_virtual_service_uuid_and_status(controller_url, session, sessionid, csrftoken, tenant, vip_name)
        if vs_uuid:
            if not vs_enabled:
                already_disabled_vips.append(vip_name)
            return vs_uuid, vs_name, vs_enabled, tenant
        return None, None, None, tenant

    # Use ThreadPoolExecutor to check VIPs concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        vip_statuses = list(executor.map(check_vip_status, [row for _, row in df.iterrows()]))

    # Notify about already disabled VIPs
    if already_disabled_vips:
        print("The following VIPs are already disabled:")
        for vip in already_disabled_vips:
            print(f"- {vip}")

    # Second pass: Enable or disable VIPs based on user input
    def process_vip(vip_info):
        vs_uuid, vs_name, vs_enabled, tenant = vip_info
        if vs_uuid and ((enable and not vs_enabled) or (not enable and vs_enabled)):
            modify_virtual_service(controller_url, session, sessionid, csrftoken, tenant, vs_uuid, vs_name, enable)

    # Process enabling/disabling VIPs concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_vip, vip_statuses)

if __name__ == "__main__":
    manage_vips_from_csv()
