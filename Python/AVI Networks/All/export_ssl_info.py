import requests
import json
import getpass  # Secure password input
import os

# Disable SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings()

# Function to authenticate and get session token and CSRF token
def authenticate(controller_url: str, username: str, password: str):
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

# Function to retrieve all tenant UUIDs with pagination
def get_all_tenants(controller_url: str, session: requests.Session, sessionid: str, csrftoken: str):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json;charset=UTF-8',
        'cookie': f'sessionid={sessionid}; csrftoken={csrftoken}',
        'x-avi-useragent': 'UI',
        'x-csrftoken': csrftoken,
        'x-avi-version': '22.1.6'
    }
    tenant_url = f'{controller_url}/api/tenant'
    tenant_dict = {"admin": "admin"}  # Include the admin tenant as a default

    while tenant_url:
        try:
            response = session.get(tenant_url, headers=headers, verify=False)
            response.raise_for_status()
            tenants_data = response.json()
            tenants = tenants_data.get('results', [])
            for tenant in tenants:
                tenant_name = tenant.get('name')
                tenant_uuid = tenant.get('uuid')
                if tenant_name and tenant_uuid:
                    tenant_dict[tenant_name] = tenant_uuid

            # Update tenant_url for next page if exists, otherwise None
            tenant_url = tenants_data.get('next')
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving tenants: {e}")
            return {}

    return tenant_dict

# Function to fetch SSL certificates with pagination and save the raw JSON response per tenant
def fetch_and_save_ssl_certificates(controller_url: str, session: requests.Session, sessionid: str, csrftoken: str, tenant_dict: dict):
    os.makedirs("tenant_certificates", exist_ok=True)  # Create directory for output files

    for tenant_name, tenant_uuid in tenant_dict.items():
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'cookie': f'sessionid={sessionid}; csrftoken={csrftoken}',
            'x-avi-tenant-uuid': tenant_uuid,
            'x-avi-useragent': 'UI',
            'x-csrftoken': csrftoken,
            'x-avi-version': '22.1.6'
        }
        
        cert_url = f'{controller_url}/api/tenant/{tenant_uuid}/sslkeyandcertificate/?export_key=true'
        certificates = []
        
        while cert_url:
            try:
                response = session.get(cert_url, headers=headers, verify=False)
                response.raise_for_status()
                cert_data = response.json()
                certificates.extend(cert_data.get('results', []))

                # Update cert_url for next page if exists, otherwise None
                cert_url = cert_data.get('next')
            except requests.exceptions.RequestException as e:
                print(f"Error retrieving SSL certificates for tenant '{tenant_name}': {e}")
                cert_url = None

        # Save the raw response for each tenant to a separate JSON file
        output_file = f'tenant_certificates/{tenant_name}_ssl_certificates.json'
        with open(output_file, 'w') as file:
            json.dump(certificates, file, indent=4)

        print(f"SSL certificates for tenant '{tenant_name}' have been saved to {output_file}")

# Main function to run the script
def main():
    # Prompt for the controller IP
    controller_ip = input("Enter the AVI Controller IP (e.g., 10.5.107.33): ")
    controller_url = f'https://{controller_ip}'

    # Prompt for username and password
    username = input("Enter your AVI username: ")
    password = getpass.getpass("Enter your AVI password: ")

    # Authenticate and get session token and CSRF token
    sessionid, csrftoken, session = authenticate(controller_url, username, password)
    if not sessionid or not csrftoken:
        print("Login failed.")
        return

    # Retrieve all tenants and their UUIDs
    tenant_dict = get_all_tenants(controller_url, session, sessionid, csrftoken)
    if not tenant_dict:
        print("Failed to retrieve tenants.")
        return

    # Fetch SSL certificates for each tenant and save raw data to JSON files
    fetch_and_save_ssl_certificates(controller_url, session, sessionid, csrftoken, tenant_dict)

if __name__ == "__main__":
    main()
