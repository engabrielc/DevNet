import aiohttp
import asyncio
import csv
import getpass
import ssl
import certifi

# AVI Controller Information
controller_ip = input("Enter the AVI Controller IP (e.g., 10.200.0.12) or FQDN: ")
controller_url = f'https://{controller_ip}'
username = input("Enter your AVI username: ")
password = getpass.getpass("Enter your AVI password: ")

# Disable SSL warnings (optional for self-signed certificates)
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Output CSV File
output_file = 'virtual_services_with_extended_info.csv'

# Function to authenticate and get session token asynchronously
async def get_session_token(session, username, password):
    async with session.post(f'{controller_url}/login', data={'username': username, 'password': password}, ssl=ssl_context) as response:
        if response.status == 200:
            return response.cookies.get('sessionid').value
        return None

# Function to get all tenants asynchronously
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

# Function to get virtual services for a tenant asynchronously
async def get_virtual_services(session, session_token, tenant_name, tenant_uuid):
    url = f'{controller_url}/api/tenant/{tenant_uuid}/virtualservice' if tenant_uuid != 'admin' else f'{controller_url}/api/tenant/admin/virtualservice'
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

# Function to get Health Score information for a virtual service asynchronously
async def get_health_score(session, session_token, tenant_uuid, vs_uuid):
    url = f'{controller_url}/api/tenant/{tenant_uuid}/analytics/healthscore/virtualservice/{vs_uuid}'
    async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
        if response.status == 200:
            health_data = await response.json()
            value = health_data.get("series", [{}])[0].get("data", [{}])[0].get("value", "N/A")
            oper_state = health_data.get("series", [{}])[0].get("data", [{}])[0].get("performance_score", {}).get("virtualservice_performance", {}).get("oper_state", "Unknown")
            return value, oper_state
    return "N/A", "Unknown"

# Function to get pool information, including server IPs, ports, and LB algorithm asynchronously
async def get_pool_info(session, session_token, tenant_uuid, pool_ref):
    if not pool_ref:
        return "No Pool", 'No Port', 'Unknown', []
    
    pool_uuid = pool_ref.split('/')[-1]
    url = f'{controller_url}/api/tenant/{tenant_uuid}/pool/{pool_uuid}'
    async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
        if response.status == 200:
            pool_data = await response.json()
            default_server_port = pool_data.get('default_server_port', 'No Port')
            lb_algorithm = pool_data.get('lb_algorithm', 'Unknown')
            servers = [
                {
                    "ip": server['ip']['addr'],
                    "port": server.get('port', default_server_port)
                }
                for server in pool_data.get('servers', [])
            ]
            return pool_data.get('name', 'Unknown'), default_server_port, lb_algorithm, servers
    return "No Pool", 'No Port', 'Unknown', []

# Function to get pool group information and collect associated pool details asynchronously
async def get_pool_group_info(session, session_token, tenant_uuid, pool_group_ref):
    if not pool_group_ref:
        return [("No Pool Group", 'No Port', 'Unknown', [])]
    
    pool_group_uuid = pool_group_ref.split('/')[-1]
    url = f'{controller_url}/api/tenant/{tenant_uuid}/poolgroup/{pool_group_uuid}'
    async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
        if response.status == 200:
            pool_group_data = await response.json()
            # Collect pool information for each member in the pool group
            tasks = [get_pool_info(session, session_token, tenant_uuid, member['pool_ref']) for member in pool_group_data.get('members', [])]
            pool_info = await asyncio.gather(*tasks)
            return pool_info
    return [("No Pool Group", 'No Port', 'Unknown', [])]

# Function to format VS ports
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

# Function to process a virtual service and collect data asynchronously
async def process_virtual_service(session, session_token, tenant_name, tenant_uuid, vs, virtual_service_data):
    vs_name = vs['name']
    vs_status = "ENABLED" if vs['enabled'] else "DISABLED"
    vsvip_ref = vs.get('vsvip_ref')
    vip_ip = await get_vip_ip(session, session_token, tenant_uuid, vsvip_ref)
    vs_ports = get_vs_port_format(vs.get('services', []))

    # Get operational state and value for health score
    value, oper_state = await get_health_score(session, session_token, tenant_uuid, vs.get('uuid'))

    # Check for Pool Group or individual Pool and get details accordingly
    pool_group_ref = vs.get('pool_group_ref')
    pool_ref = vs.get('pool_ref')

    if pool_group_ref:
        pool_info = await get_pool_group_info(session, session_token, tenant_uuid, pool_group_ref)
    elif pool_ref:
        pool_info = [await get_pool_info(session, session_token, tenant_uuid, pool_ref)]
    else:
        pool_info = [("No Pool", 'No Port', 'Unknown', [])]

    for pool_name, default_server_port, lb_algorithm, servers in pool_info:
        server_ips = ", ".join([server['ip'] for server in servers]) if servers else "No Servers"
        server_ports = ", ".join([str(server['port']) for server in servers]) if servers else "No Ports"
        
        virtual_service_data.append([
            tenant_name, vs_name, vip_ip, vs_status, pool_name, lb_algorithm, server_ips, server_ports, vs_ports, value, oper_state
        ])

# Main function to handle tenants and export data
async def main():
    async with aiohttp.ClientSession() as session:
        session_token = await get_session_token(session, username, password)
        if not session_token:
            print("Failed to authenticate.")
            return

        tenants = await get_all_tenants(session, session_token)
        virtual_service_data = []

        # Process tenants
        for tenant in tenants:
            tenant_name = tenant['name']
            tenant_uuid = tenant['uuid'] if tenant_name != 'admin' else 'admin'
            virtual_services = await get_virtual_services(session, session_token, tenant_name, tenant_uuid)

            # Process virtual services concurrently
            tasks = [process_virtual_service(session, session_token, tenant_name, tenant_uuid, vs, virtual_service_data) for vs in virtual_services]
            await asyncio.gather(*tasks)

        export_to_csv(virtual_service_data)
        print("Data exported to 'virtual_services_with_extended_info.csv' successfully!")

# Function to write data to CSV
def export_to_csv(data, file_name='virtual_services_with_extended_info.csv'):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Tenant', 'VIP Name', 'IP', 'Status', 'Pool Name', 'LB Algorithm', 'Server IPs', 'Server Ports', 'VS Ports', 'Value', 'Oper State'])
        writer.writerows(data)

# Run the main function
asyncio.run(main())
