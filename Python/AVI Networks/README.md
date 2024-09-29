
# VIP Management Script for AVI Controller

## Purpose
This script allows you to manage Virtual IPs (VIPs) in an AVI Controller environment. It supports both **disabling** and **enabling** (rollback) of VIPs for multiple tenants and VIPs listed in a CSV file.

Before performing any actions, the script checks if any VIPs are already disabled and lists them. After listing the already-disabled VIPs, it proceeds to either disable or enable the VIPs based on your input.

### Key Features:
1. **Authentication**: The script prompts for your AVI Controller credentials (IP address, username, and password) and retrieves the session token and CSRF token for authentication.
2. **Pre-check for Disabled VIPs**: Before performing any operations, the script lists all VIPs that are already disabled.
3. **Disable or Enable VIPs**: Based on your input, the script will either disable or enable the VIPs listed in the CSV file.
4. **CSV Input**: The script reads the tenant and VIP names from a CSV file (`virtual_services.csv`), making it easy to manage multiple VIPs across different tenants.

## Prerequisites
- You must have access to the AVI Controller and the necessary permissions to disable/enable VIPs.
- The script expects a CSV file named `virtual_services.csv` in the same directory. The CSV should contain the following columns:
  - `Tenant`: The name of the tenant.
  - `VIP Name`: The name of the VIP.

### Example CSV file (`virtual_services.csv`):
```csv
Tenant,VIP Name
tenantA,vip-name-1
tenantB,vip-name-2
```

## How to Use the Script

### 1. Run the Script
- Run the script using Python.
  
```bash
python manage_vips.py
```

### 2. Enter the AVI Controller Details
The script will prompt you for the following details:
- **AVI Controller IP**: The IP address of your AVI Controller (e.g., `https://192.168.1.100`).
- **AVI Username**: Your AVI Controller username.
- **AVI Password**: Your AVI Controller password.

### 3. Select the Action
The script will then ask you to select whether you want to:
- **Disable** the VIPs, or
- **Enable** (rollback) the VIPs.

Type either `disable` or `enable` based on the action you want to perform.

### 4. Review Already Disabled VIPs
Before proceeding, the script will list any VIPs that are already disabled.

### 5. Execute the Operation
The script will proceed with disabling or enabling the VIPs as per your selection. 

### Example Output
```bash
Enter the AVI Controller IP (e.g., 192.168.1.100): 192.168.1.100
Enter your AVI username: admin
Enter your AVI password: ******
Do you want to disable the VIPs or enable them? (type 'disable' or 'enable'): disable

The following VIPs are already disabled:
 - vip-name-1 (Tenant: tenantA)

Proceeding with the normal operation...

Virtual Service 'vip-name-2' disabled successfully for tenant 'tenantB'.
```

## Notes
- Make sure to update the `virtual_services.csv` file with the correct tenant and VIP names before running the script.
- This script will only affect the VIPs listed in the CSV file and does not make any changes to other resources.

## Error Handling
If a VIP cannot be disabled or enabled (e.g., due to a missing VIP or incorrect permissions), the script will print an error message with the details.
