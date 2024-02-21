import os

# Flushing the output file before use
with open("ip_output.txt","w") as file:
        pass

with open("ip_list.txt") as file:
    ipList = file.read()
    ipList = ipList.splitlines()
    print(ipList[:])
    # ping for each ip in the file
for ip in ipList:
    response = os.popen(f"ping -n 2 {ip} ").read()
    # Pinging each IP address 2 times

    #saving some ping output details to output file
    if " TTL=" not in response:
            print(response)
            f = open("ip_output.txt","a")
            f.write(str(ip) + ' link is down'+'\n')
            f.close()
    else:
            print(response)
            f = open("ip_output.txt","a")
            f.write(str(ip) + ' is up '+'\n')
            f.close()

# print output file to screen
with open("ip_output.txt") as file:
    output = file.read()
    f.close()
    print(output)
