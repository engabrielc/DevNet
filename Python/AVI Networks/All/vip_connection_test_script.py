import aiohttp
import asyncio
import csv
import socket
import ssl
import certifi
import time
import getpass
import logging

# Set up basic logging for VIP processing notifications
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# File paths
vs_input_file_path = 'virtual_services_validations_specific_ports.csv'
output_results_file_path = 'connection_test_results.txt'

# AVI Controller details
controller_ip = input("Enter the AVI Controller IP (e.g., 10.200.0.12) or FQDN: ")
controller_url = f'https://{controller_ip}'
username = input("Enter your AVI username: ")
password = getpass.getpass("Enter your AVI password: ")

# SSL configuration for self-signed certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Authenticate and obtain session token
async def get_session_token(session, username, password):
    url = f'{controller_url}/login'
    async with session.post(url, data={'username': username, 'password': password}, ssl=ssl_context) as response:
        if response.status == 200:
            return response.cookies.get('sessionid').value
    return None

# Fetch all tenants and filter by name to find tenant UUID
async def get_all_tenants(session, session_token):
    tenants = []
    url = f'{controller_url}/api/tenant'
    while url:
        async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
            if response.status == 200:
                data = await response.json()
                tenants.extend(data.get('results', []))
                url = data.get('next')
            else:
                url = None
    return tenants

async def get_tenant_uuid(session, session_token, tenant_name):
    tenants = await get_all_tenants(session, session_token)
    for tenant in tenants:
        if tenant['name'] == tenant_name:
            return tenant['uuid']
    return None

# Fetch all virtual services for a tenant and filter by name to find virtual service UUID
async def get_virtual_services(session, session_token, tenant_uuid):
    virtual_services = []
    url = f'{controller_url}/api/tenant/{tenant_uuid}/virtualservice'
    while url:
        async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
            if response.status == 200:
                data = await response.json()
                virtual_services.extend(data.get('results', []))
                url = data.get('next')
            else:
                url = None
    return virtual_services

async def get_virtual_service_uuid(session, session_token, tenant_uuid, vip_name):
    virtual_services = await get_virtual_services(session, session_token, tenant_uuid)
    for vs in virtual_services:
        if vs['name'] == vip_name:
            return vs['uuid']
    return None

# Retrieve VIP IP from vsvip_ref
async def get_vip_ip(session, session_token, tenant_uuid, vsvip_ref):
    if not vsvip_ref:
        return "No VIP"
    vsvip_uuid = vsvip_ref.split('/')[-1]
    url = f'{controller_url}/api/tenant/{tenant_uuid}/vsvip/{vsvip_uuid}'
    async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
        if response.status == 200:
            vsvip_data = await response.json()
            vip_data = vsvip_data.get('vip', [])
            if vip_data and 'ip_address' in vip_data[0]:
                return vip_data[0]['ip_address']['addr']
    return "No VIP"

# Format and retrieve VS ports
def get_vs_port_format(services):
    if not services:
        return "No Port"
    ports = []
    for service in services:
        port = service.get('port')
        port_range_end = service.get('port_range_end', port)
        if port == port_range_end:
            ports.append(str(port))
        else:
            ports.append(f"{port}-{port_range_end}")
    return ", ".join(ports)

# Fetch virtual service details
async def fetch_vip_details(session, session_token, tenant_uuid, vs_uuid):
    url = f"{controller_url}/api/tenant/{tenant_uuid}/virtualservice/{vs_uuid}"
    async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
        if response.status == 200:
            data = await response.json()
            vsvip_ref = data.get('vsvip_ref')
            services = data.get('services', [])
            
            # Retrieve IP and format ports
            ip_address = await get_vip_ip(session, session_token, tenant_uuid, vsvip_ref)
            ports = get_vs_port_format(services)
            return ip_address, ports
    return None, None

# Perform a connection test
def test_connection(ip, port, timeout=2):
    try:
        with socket.create_connection((ip, int(port)), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, socket.error):
        return False

# Main async function to execute tests
async def main():
    async with aiohttp.ClientSession() as session:
        # Get session token
        session_token = await get_session_token(session, username, password)
        if not session_token:
            print("Authentication failed. Exiting.")
            return

        # Read tenant and VIP name from CSV
        with open(vs_input_file_path, 'r') as f:
            reader = csv.DictReader(f)
            vs_records = [row for row in reader]

        # Write results
        with open(output_results_file_path, 'w') as results_file:
            results_file.write("Connection Test Results\n")
            results_file.write("====================================\n")

            for record in vs_records:
                vip_name = record['VIP Name']
                tenant = record['Tenant']
                print(f"Processing VIP: {vip_name}")

                # Retrieve tenant UUID
                tenant_uuid = await get_tenant_uuid(session, session_token, tenant)
                if not tenant_uuid:
                    results_file.write(f"Tenant: {tenant}, VIP: {vip_name} - Tenant UUID not found.\n")
                    continue

                # Retrieve virtual service UUID
                vs_uuid = await get_virtual_service_uuid(session, session_token, tenant_uuid, vip_name)
                if not vs_uuid:
                    results_file.write(f"Tenant: {tenant}, VIP: {vip_name} - Virtual service UUID not found.\n")
                    continue

                # Fetch VIP details
                ip_address, ports = await fetch_vip_details(session, session_token, tenant_uuid, vs_uuid)
                if ip_address and ports and ports != "No Port":
                    for port in ports.split(', '):
                        start_time = time.time()
                        success = test_connection(ip_address, port.strip())
                        duration = time.time() - start_time
                        status = "Success" if success else "Failed"
                        results_file.write(f"Tenant: {tenant}, VIP: {vip_name}, IP: {ip_address}, Port: {port}, "
                                           f"Status: {status}, Time: {duration:.2f} sec\n")
                else:
                    results_file.write(f"Tenant: {tenant}, VIP: {vip_name} - Extended information not found.\n")

        print(f"Connection test results saved to {output_results_file_path}.")

# Run main function
asyncio.run(main())
