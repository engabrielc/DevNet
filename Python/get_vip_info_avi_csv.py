#This script connects to the AVI controller to retrieve the Tenant, VIP name, IP, and status for all VIPs.
 

import requests
import csv
import getpass

# AVI Controller Information
controller_url = 'https://<AVI_CONTROLLER_IP_OR_FQDN>'

# Disable SSL warnings (optional for self-signed certificates)
requests.packages.urllib3.disable_warnings()

# Function to authenticate and get session token
def get_session_token(username, password):
    response = requests.post(f'{controller_url}/login', data={'username': username, 'password': password}, verify=False)
    return response.cookies['sessionid'] if response.status_code == 200 else None

# Function to get all tenants with pagination
def get_all_tenants(session_token):
    tenants = []
    url = f'{controller_url}/api/tenant'
    while url:
        response = requests.get(url, cookies={'sessionid': session_token}, verify=False)
        if response.status_code == 200:
            data = response.json()
            tenants.extend(data['results'])
            url = data.get('next')
        else:
            url = None
    return tenants

# Function to get virtual services for a tenant (handling pagination)
def get_virtual_services(session_token, tenant_name, tenant_uuid):
    url = f'{controller_url}/api/tenant/{tenant_uuid}/virtualservice' if tenant_name != 'admin' else f'{controller_url}/api/tenant/{tenant_name}/virtualservice'
    virtual_services = []
    while url:
        response = requests.get(url, cookies={'sessionid': session_token}, verify=False)
        if response.status_code == 200:
            data = response.json()
            virtual_services.extend(data['results'])
            url = data.get('next')
        else:
            url = None
    return virtual_services

# Function to get the VIP IP from the vsvip_ref
def get_vip_ip(session_token, tenant_uuid, vsvip_ref):
    vsvip_uuid = vsvip_ref.split('/')[-1]  # Extract UUID from vsvip_ref URL
    url = f'{controller_url}/api/tenant/{tenant_uuid}/vsvip/{vsvip_uuid}'
    response = requests.get(url, cookies={'sessionid': session_token}, verify=False)
    if response.status_code == 200:
        vsvip_data = response.json()
        vip_data = vsvip_data.get('vip', [])
        if vip_data and 'ip_address' in vip_data[0]:
            return vip_data[0]['ip_address']['addr']
    return None

# Function to write data to CSV
def export_to_csv(data, file_name='virtual_services.csv'):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Tenant', 'VIP Name', 'IP', 'Status'])
        writer.writerows(data)

# Main function to authenticate, get tenants, and export virtual service data to CSV
def main():
    # Prompt for username and password
    username = input("Enter your AVI username: ")
    password = getpass.getpass("Enter your AVI password: ")

    session_token = get_session_token(username, password)
    if not session_token:
        print("Login failed")
        return

    tenants = get_all_tenants(session_token)
    virtual_service_data = []

    for tenant in tenants:
        tenant_name = tenant['name']
        tenant_uuid = tenant['uuid']
        virtual_services = get_virtual_services(session_token, tenant_name, tenant_uuid)

        for vs in virtual_services:
            vs_name = vs['name']
            vs_status = "ENABLED" if vs['enabled'] else "DISABLED"
            vsvip_ref = vs.get('vsvip_ref')
            vip_ip = get_vip_ip(session_token, tenant_uuid, vsvip_ref) if vsvip_ref else "No VIP"
            
            # Collect the data for each virtual service
            virtual_service_data.append([tenant_name, vs_name, vip_ip, vs_status])

    # Export data to CSV
    export_to_csv(virtual_service_data)

    print(f"Data exported to 'virtual_services.csv' successfully!")

if __name__ == "__main__":
    main()
