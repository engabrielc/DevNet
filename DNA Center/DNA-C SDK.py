from dnacentersdk import api
import json
import time
import calendar

dna = api.DNACenterAPI(base_url="https://sandboxdnac2.cisco.com", username= "devnetuser" , password= "Cisco123!", verify=False)

#Get VLANS

vlans = dna.topology.get_vlan_details()
for vlan in vlans.response:
    print (vlan)




