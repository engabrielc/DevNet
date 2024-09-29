import requests
import getpass
import pandas as pd

# Disable SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings()

# Function to authenticate and get session token and CSRF token
def authenticate(controller_url, username, password):
    login_url = f'{controller_url}/login'
    try:
        with requests.Session() as session:
            response = session.post(login_url, data={'username': username, 'password': password}, verify=False)
            response.raise_for_status()  # Ensure login is successful
            cookies = response.cookies.get_dict()
            sessionid = cookies.get('sessionid')
            csrftoken = cookies.get('csrftoken')

            if sessionid and csrftoken:
                print("Authentication successful!")
                return sessionid, csrftoken, session  # Return session to keep cookies alive
            else:
                print("Failed to retrieve session or CSRF token.")
                return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error during authentication: {e}")
        return None, None, None

# Function to get the UUID and status of a virtual service by VIP name
def get_virtual_service_uuid_and_status(controller_url, session, sessionid, csrftoken, tenant_name, vip_name):
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

# Function to disable a virtual service using its UUID and tenant
def disable_virtual_service(controller_url, session, sessionid, csrftoken, tenant_name, vs_uuid, vs_name):
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

    payload = {
        "replace": {
            "enabled": False  # Disable the virtual service
        }
    }

    try:
        response = session.patch(vs_url, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        print(f"Virtual Service '{vs_name}' disabled successfully for tenant '{tenant_name}'.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to disable Virtual Service '{vs_name}' for tenant '{tenant_name}'. Error: {e}")

# Function to enable a virtual service (Rollback)
def enable_virtual_service(controller_url, session, sessionid, csrftoken, tenant_name, vs_uuid, vs_name):
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

    payload = {
        "replace": {
            "enabled": True  # Re-enable the virtual service
        }
    }

    try:
        response = session.patch(vs_url, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        print(f"Virtual Service '{vs_name}' re-enabled successfully for tenant '{tenant_name}'.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to re-enable Virtual Service '{vs_name}' for tenant '{tenant_name}'. Error: {e}")

# Main function to prompt for disable/enable action and execute accordingly
def manage_vips_from_csv():
    # Prompt for the controller IP
    controller_ip = input("Enter the AVI Controller IP (e.g., 192.168.1.100): ")
    controller_url = f'https://{controller_ip}'

    # Prompt for username and password
    username = input("Enter your AVI username: ")
    password = getpass.getpass("Enter your AVI password: ")

    # Ask whether the user wants to disable or enable (rollback)
    action = input("Do you want to disable the VIPs or enable them? (type 'disable' or 'enable'): ").strip().lower()

    # Authenticate and get session token and CSRF token
    sessionid, csrftoken, session = authenticate(controller_url, username, password)
    if not sessionid or not csrftoken:
        print("Login failed.")
        return

    # Load CSV data with tenants and VIP names
    csv_file_path = 'virtual_services.csv'  # Update this path if needed
    df = pd.read_csv(csv_file_path)

    already_disabled_vips = []

    # First pass: Check which VIPs are already disabled and list them
    for _, row in df.iterrows():
        tenant = row['Tenant']
        vip_name = row['VIP Name']

        # Get the UUID, name, and status of the virtual service based on the VIP name
        vs_uuid, vs_name, vs_enabled = get_virtual_service_uuid_and_status(controller_url, session, sessionid, csrftoken, tenant, vip_name)
        if vs_uuid and not vs_enabled:  # If it's already disabled
            already_disabled_vips.append((vs_name, tenant))

    # List all VIPs that are already disabled
    if already_disabled_vips:
        print("\nThe following VIPs are already disabled:")
        for vip_name, tenant_name in already_disabled_vips:
            print(f" - {vip_name} (Tenant: {tenant_name})")
        print("\nProceeding with the normal operation...\n")

    # Second pass: Proceed with normal disable/enable operation
    for _, row in df.iterrows():
        tenant = row['Tenant']
        vip_name = row['VIP Name']

        # Get the UUID, name, and status of the virtual service based on the VIP name
        vs_uuid, vs_name, vs_enabled = get_virtual_service_uuid_and_status(controller_url, session, sessionid, csrftoken, tenant, vip_name)
        if vs_uuid:
            if action == 'disable' and vs_enabled:
                # Disable the virtual service only if it's enabled
                disable_virtual_service(controller_url, session, sessionid, csrftoken, tenant, vs_uuid, vs_name)
            elif action == 'enable' and not vs_enabled:
                # Re-enable the virtual service (rollback) only if it's disabled
                enable_virtual_service(controller_url, session, sessionid, csrftoken, tenant, vs_uuid, vs_name)
            else:
                print(f"Virtual Service '{vs_name}' for tenant '{tenant}' is already in the desired state.")

if __name__ == "__main__":
    manage_vips_from_csv()
