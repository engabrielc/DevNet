import requests
import urllib3
from getpass import getpass
from openpyxl import Workbook

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# List of vADCs to query
vadcs = {
    "Name_on_the_Sheet_vADC_1": "X.X.X.X",
   
    "Name_on_the_Sheet_vADC_2": "Z.Z.Z.Z"
    
}

# Prompt for credentials
username = input("Username: ")
password = getpass("Password: ")

# Create Excel workbook
wb = Workbook()
# Remove default sheet
default_sheet = wb.active
wb.remove(default_sheet)

for name, ip in vadcs.items():
    url = f"https://{ip}/config/SlbNewCfgEnhVirtServerTable"

    print(f"\nQuerying {name} ({ip}) ...")

    response = requests.get(
        url,
        auth=(username, password),
        verify=False,
        headers={"Accept": "application/json"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f" Failed to authenticate or query {name}")
        continue

    data = response.json()

    # Create new sheet for this vADC
    ws = wb.create_sheet(title=name)
    ws.append(["VirtServerIndex", "VirtServerIpAddress"])

    for vs in data.get("SlbNewCfgEnhVirtServerTable", []):
        ws.append([
            vs.get("VirtServerIndex"),
            vs.get("VirtServerIpAddress")
        ])

# Save Excel file
output_file = "virtual_servers_all_vadcs.xlsx"
wb.save(output_file)

print(f"\n Excel export complete: {output_file}")
