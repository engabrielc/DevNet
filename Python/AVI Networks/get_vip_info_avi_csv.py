# Script to retrieve virtual service info with added health data ("value" and "oper_state")

import aiohttp
import asyncio
import csv
import getpass
import ssl
import certifi

# AVI Controller Information
controller_ip = input("Enter the AVI Controller IP (e.g., 10.5.107.33) or FQDN: ")
controller_url = f'https://{controller_ip}'
username = input("Enter your AVI username: ")
password = getpass.getpass("Enter your AVI password: ")

# Disable SSL warnings (optional for self-signed certificates)
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Output CSV File
output_file = 'virtual_services_with_health_data.csv'

# Function to authenticate and get session token asynchronously
async def get_session_token(session, username, password):
    async with session.post(f'{controller_url}/login', data={'username': username, 'password': password}, ssl=ssl_context) as response:
        if response.status == 200:
            return response.cookies.get('sessionid').value
        return None

# Function to get all tenants with pagination asynchronously
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

# Function to get virtual services for a tenant asynchronously (handling pagination)
async def get_virtual_services(session, session_token, tenant_name, tenant_uuid):
    url = f'{controller_url}/api/tenant/{tenant_uuid}/virtualservice' if tenant_name != 'admin' else f'{controller_url}/api/tenant/{tenant_name}/virtualservice'
    virtual_services = []
    while url:
        async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
            if response.status == 200:
                data = await response.json()
                virtual_services.extend(data.get('results', []))
                url = data.get('next')
            else:
                url = None
    return virtual_services

# Function to retrieve the health score data for "value" and "oper_state" of each virtual service
async def get_vs_health_info(session, session_token, tenant_uuid, vs_uuid):
    url = f"{controller_url}/api/tenant/{tenant_uuid}/analytics/healthscore/virtualservice/{vs_uuid}"
    async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
        if response.status == 200:
            data = await response.json()
            health_data = data.get('series', [{}])[0].get('data', [{}])[0]
            vs_value = health_data.get('value', None)
            oper_state = health_data.get('performance_score', {}).get('virtualservice_performance', {}).get('oper_state', None)
            return vs_value, oper_state
        return None, None

# Function to get the VIP IP from the vsvip_ref asynchronously
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

# Function to format virtual service port details
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

# Main function to authenticate, get tenants, and export virtual service data to CSV
async def main():
    async with aiohttp.ClientSession() as session:
        session_token = await get_session_token(session, username, password)
        if not session_token:
            print("Login failed")
            return

        tenants = await get_all_tenants(session, session_token)
        virtual_service_data = []

        tasks = [process_tenant(session, session_token, tenant, virtual_service_data) for tenant in tenants]
        await asyncio.gather(*tasks)

        export_to_csv(virtual_service_data)
        print(f"Data exported to '{output_file}' successfully!")

# Function to process each tenant's virtual services
async def process_tenant(session, session_token, tenant, virtual_service_data):
    tenant_name = tenant['name']
    tenant_uuid = tenant['uuid']
    virtual_services = await get_virtual_services(session, session_token, tenant_name, tenant_uuid)

    tasks = [process_virtual_service(session, session_token, tenant_name, tenant_uuid, vs, virtual_service_data) for vs in virtual_services]
    await asyncio.gather(*tasks)

# Function to process each virtual service and collect data asynchronously
async def process_virtual_service(session, session_token, tenant_name, tenant_uuid, vs, virtual_service_data):
    vs_name = vs['name']
    vs_status = "ENABLED" if vs['enabled'] else "DISABLED"
    vsvip_ref = vs.get('vsvip_ref')
    vip_ip = await get_vip_ip(session, session_token, tenant_uuid, vsvip_ref)

    vs_ports = get_vs_port_format(vs.get('services', []))
    
    # Get health information for the virtual service
    vs_value, oper_state = await get_vs_health_info(session, session_token, tenant_uuid, vs['uuid'])

    # Pool information handling as before
    pool_info = [("No Pool", 'No Port', 'Unknown', [])]  # Placeholder for actual pool information

    for pool_name, default_server_port, lb_algorithm, servers in pool_info:
        server_ips = ", ".join([server['ip'] for server in servers]) if servers else "No Servers"
        server_ports = ", ".join([str(server['port']) for server in servers]) if servers else "No Ports"
        
        virtual_service_data.append([
            tenant_name, vs_name, vip_ip, vs_status, pool_name, lb_algorithm, server_ips, server_ports, vs_ports, vs_value, oper_state
        ])

# CSV export function with additional columns for "value" and "oper_state"
def export_to_csv(data, file_name=output_file):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Tenant', 'VIP Name', 'IP', 'Status', 'Pool Name', 'LB Algorithm', 'Server IPs', 'Server Ports', 'VS Ports', 'Value', 'Oper State'])
        writer.writerows(data)

if __name__ == "__main__":
    asyncio.run(main())

