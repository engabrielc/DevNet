
# VIP Connection Test Script

This script connects to an AVI Controller and performs connectivity tests on specified VIPs (Virtual IPs) based on details provided in a `virtual_services.csv` file. The script:
1. Authenticates to the AVI Controller.
2. Fetches tenant and virtual service UUIDs.
3. Retrieves the VIP IP address and port information.
4. Tests connectivity to each VIP's IP and port and logs the results.

## Prerequisites

- Python 3.7+
- `aiohttp` library for asynchronous HTTP requests.
- `certifi` library for SSL certificates.

## Setup

1. Ensure the required Python packages are installed:
   ```bash
   pip install aiohttp certifi
   ```

2. Prepare a `virtual_services.csv` file in the same directory with the following columns:
   ```
   Tenant,VIP Name
   ```

3. Place the script and the `virtual_services.csv` file in the same directory.

## Usage

1. Run the script:
   ```bash
   python3 script_name.py
   ```

2. Provide the following inputs when prompted:
   - AVI Controller IP or FQDN
   - AVI Username
   - AVI Password

3. The script will:
   - Authenticate to the AVI Controller.
   - Retrieve the UUIDs for each tenant and virtual service.
   - Fetch IP and port details for each VIP.
   - Test connectivity to each IP and port combination.

4. Results will be saved in `connection_test_results.txt`.

## Output

- **File**: `connection_test_results.txt`
- **Format**:
  ```
  Connection Test Results
  ====================================
  Tenant: <Tenant Name>, VIP: <VIP Name>, IP: <IP Address>, Port: <Port>, Status: <Success/Failed>, Time: <Time in sec>
  ```

## Script Breakdown

### Functions

- **get_session_token**: Authenticates to the AVI Controller and retrieves a session token.
- **get_all_tenants**: Retrieves a list of tenants from the AVI Controller.
- **get_tenant_uuid**: Finds the UUID for a specified tenant.
- **get_virtual_services**: Retrieves a list of virtual services for a tenant.
- **get_virtual_service_uuid**: Finds the UUID for a specified virtual service.
- **get_vip_ip**: Retrieves the IP address of the VIP based on `vsvip_ref`.
- **get_vs_port_format**: Formats and retrieves the ports for each service.
- **fetch_vip_details**: Combines IP and port retrieval.
- **test_connection**: Tests connectivity to a specified IP and port.
- **process_vip**: Processes each VIP, performing the connection test and logging results.

### Main Workflow

1. **Authentication**: Prompts the user to enter AVI Controller details, authenticates, and retrieves a session token.
2. **CSV Processing**: Reads the `virtual_services.csv` file to get a list of VIPs.
3. **UUID Retrieval**: Fetches the UUIDs for tenants and virtual services based on the CSV input.
4. **Connection Testing**: For each VIP, tests connectivity to each port and logs results in `connection_test_results.txt`.

## Example Output

```
Connection Test Results
====================================
Tenant: ExampleTenant, VIP: example-vip-1, IP: 192.168.1.10, Port: 80, Status: Success, Time: 0.09 sec
Tenant: ExampleTenant, VIP: example-vip-2 - Extended information not found.
Tenant: ExampleTenant, VIP: example-vip-3, IP: 192.168.1.11, Port: 80, Status: Failed, Time: 21.03 sec
```

## Notes

- **Timeouts**: The connection test timeout is set to 2 seconds.
- **Errors**: If a UUID or connection is unavailable, the error is logged in the results file.
- **SSL**: The script uses `certifi` for SSL certificates. Adjust SSL settings if using self-signed certificates.

