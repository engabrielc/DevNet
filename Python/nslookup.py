import os

# Read in list of IP addresses from file
with open('ip_list.txt', 'r') as f:
    ip_list = [line.strip() for line in f]

# Perform nslookup for each IP address and create a dictionary of results
results = {}
for ip in ip_list:
    output = os.popen(f"nslookup {ip}").read().splitlines()
    for line in output:
        if line.startswith("Name:"):
            hostname = line.split()[1].rstrip('.')
            results[ip] = hostname
            break
            
#Print all the hostnames
for hostname in results.values():
    print(hostname)
