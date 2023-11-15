import requests
import getpass
import urllib3

# Disable SSL/TLS-related warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get credentials from user input
username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")

# Function to authenticate and get the token
def get_token(username, password):
    auth_url = "https://dfwdcciapic1.corp.pvt/api/aaaLogin.json" # Ensure that the correct APIC is being utilized
    auth_payload = {
        "aaaUser": {
            "attributes": {
                "name": username,
                "pwd": password
            }
        }
    }

    auth_response = requests.post(auth_url, json=auth_payload, verify=False)
    auth_data = auth_response.json()

    if auth_response.status_code == 200:
        token = auth_data["imdata"][0]["aaaLogin"]["attributes"]["token"]
        return token
    else:
        print(f"Authentication Error: {auth_response.status_code} - {auth_data}")
        return None

# List of BDs to query
bd_list = ["12", "16", "18", "197", "20", "24", "28", "3", "30", "351", "353", "506", "13"]  # Add your BDs to this list

# Function to get subnets using the token and list of BDs
def get_subnets_for_bds(token, bd_list):
    for bd in bd_list:
        url = f"https://dfwdcciapic1.corp.pvt/api/node/mo/uni/tn-DFWLegacyDC/BD-BD-{bd}.json?rsp-subtree=full&rsp-subtree-class=fvSubnet" # Change the Tenant if necessary

        headers = {
            "Cookie": f"APIC-cookie={token}"
        }

        response = requests.get(url, headers=headers, verify=False)
        data = response.json()

        if response.status_code == 200:
            try:
                subnets = data["imdata"][0]["fvBD"]["children"]

                print(f"Gateways for BD-{bd}:")
                for subnet in subnets:
                    subnet_ip = subnet["fvSubnet"]["attributes"]["ip"]

                    print(f"  IP: {subnet_ip}")

            except (KeyError, IndexError):
                print(f"BD-{bd} has no subnets or does not exist")

        else:
            print(f"Error for BD-{bd}: {response.status_code} - {data}")

# Get the token
token = get_token(username, password)

if token:
    # Use the token to get subnets for each BD in the list
    get_subnets_for_bds(token, bd_list)
