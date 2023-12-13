import requests
import getpass
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

username, password, APIC, tenant = input("Enter your username: "), getpass.getpass("Enter your password: "), "YOUR_APIC", "YOUR_TENANT"
auth_url, epg_url = f'https://{APIC}/api/aaaLogin.json', f"https://{APIC}/api/node/mo/uni/tn-{tenant}/ap-{tenant}.json?query-target=subtree&target-subtree-class=fvAEPg"
auth_payload = {"aaaUser": {"attributes": {"name": username, "pwd": password}}}

def get_token():
    return requests.post(auth_url, json=auth_payload, verify=False).json().get("imdata", [{}])[0].get("aaaLogin", {}).get("attributes", {}).get("token")

def get_vlan_names(epg_data):
    return [epg["fvAEPg"]["attributes"]["name"] for epg in epg_data.get("imdata", [])]

token = get_token()
if token:
    response = requests.get(epg_url, headers={"Cookie": f"APIC-cookie={token}"}, verify=False)
    if response.status_code == 200:
        vlan_names = sorted(get_vlan_names(response.json()), key=lambda x: int(x.split('-')[-1]))
        print(*vlan_names, sep='\n')
    else:
        print(f"Error: {response.status_code} - {response.text}")
else:
    print("Authentication failed.")
