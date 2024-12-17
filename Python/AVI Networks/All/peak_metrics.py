import aiohttp
import asyncio
import getpass
import ssl
import certifi
import csv

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
output_file = 'vips_peak_metrics.csv'

async def get_session_token(session, username, password):
    async with session.post(f'{controller_url}/login', data={'username': username, 'password': password}, ssl=ssl_context) as response:
        if response.status == 200:
            return response.cookies.get('sessionid').value
        return None

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

async def get_virtual_services(session, session_token, tenant_uuid):
    url = f'{controller_url}/api/tenant/{tenant_uuid}/virtualservice'
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

async def get_vip_ip(session, session_token, tenant_uuid, vsvip_ref):
    """Fetch the VIP IP for the virtual service."""
    if not vsvip_ref:
        return "No IP"
    vsvip_uuid = vsvip_ref.split("/")[-1]
    url = f'{controller_url}/api/tenant/{tenant_uuid}/vsvip/{vsvip_uuid}'
    async with session.get(url, cookies={'sessionid': session_token}, ssl=ssl_context) as response:
        if response.status == 200:
            vsvip_data = await response.json()
            vip_data = vsvip_data.get('vip', [])
            if vip_data and 'ip_address' in vip_data[0]:
                return vip_data[0]['ip_address']['addr']
    return "No IP"

async def get_vip_metrics(session, session_token, tenant_uuid, vs_uuid):
    url = f"{controller_url}/api/tenant/{tenant_uuid}/analytics/metrics/virtualservice/{vs_uuid}"
    params = {
        "metric_id": "l4_client.avg_bandwidth,l4_client.max_open_conns",
        "step": "86400",
        "start": "2023-11-18T00:00:00Z",
        "stop": "2024-11-18T00:00:00Z"
    }
    async with session.get(url, cookies={'sessionid': session_token}, params=params, ssl=ssl_context) as response:
        if response.status == 200:
            metrics = await response.json()
            return metrics
    return {}

async def process_virtual_service(session, session_token, tenant_name, tenant_uuid, vs, vip_data):
    vs_name = vs['name']
    vsvip_ref = vs.get('vsvip_ref')
    vip_ip = await get_vip_ip(session, session_token, tenant_uuid, vsvip_ref)  # Fetch the VIP IP
    vs_ports = ", ".join([str(service['port']) for service in vs.get('services', [])])

    metrics = await get_vip_metrics(session, session_token, tenant_uuid, vs['uuid'])
    peak_throughput = "N/A"
    peak_connections = "N/A"

    for metric in metrics.get('series', []):
        if metric.get('header', {}).get('name') == 'l4_client.avg_bandwidth':
            peak_throughput = max(
                [dp.get('value', 0) for dp in metric.get('data', []) if not dp.get('is_null', False)],
                default="N/A"
            )
        elif metric.get('header', {}).get('name') == 'l4_client.max_open_conns':
            peak_connections = max(
                [dp.get('value', 0) for dp in metric.get('data', []) if not dp.get('is_null', False)],
                default="N/A"
            )

    vip_data.append([tenant_name, vs_name, vip_ip, vs_ports, peak_throughput, peak_connections])

async def main():
    async with aiohttp.ClientSession() as session:
        session_token = await get_session_token(session, username, password)
        if not session_token:
            print("Failed to authenticate.")
            return

        tenants = await get_all_tenants(session, session_token)
        vip_data = []

        for tenant in tenants:
            tenant_name = tenant['name']
            tenant_uuid = tenant['uuid']
            virtual_services = await get_virtual_services(session, session_token, tenant_uuid)
            tasks = [process_virtual_service(session, session_token, tenant_name, tenant_uuid, vs, vip_data) for vs in virtual_services]
            await asyncio.gather(*tasks)

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Tenant', 'VIP Name', 'IP', 'Ports', 'Peak Throughput (bps)', 'Peak Connections Per Second'])
            writer.writerows(vip_data)

        print(f"Data exported to {output_file} successfully!")

asyncio.run(main())
