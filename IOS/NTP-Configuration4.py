# Python script to configure NTP settings on Cisco IOS, by Enrique Gabriel.

# Do not forget to install Netmiko (pip install Netmiko)

from netmiko import ConnectHandler

# 1. We need to define the devices that are going to receive the NTP configuration.

R1 = {

    "device_type" : "cisco_ios",
    "ip" : "192.168.1.184",
    "username" : "cisco",
    "password" : "cisco",
    "secret" : "cisco"
}

R2 = {

    "device_type" : "cisco_ios",
    "ip" : "192.168.1.185",
    "username" : "cisco",
    "password" : "cisco",
    "secret" : "cisco"
}

R3 = {

    "device_type" : "cisco_ios",
    "ip" : "192.168.1.186",
    "username" : "cisco",
    "password" : "cisco",
    "secret" : "cisco"
}

# 2. Then, we should create an array (list) in order to group the devices together.

all_routers = [R1, R2, R3]

# 3. Using a "for" loop, we are going to iterate through every device applying the NTP configuration.

for router in all_routers:
    net_connect = ConnectHandler(**router)
    net_connect.enable()
    net_connect.send_config_set(["ntp server 192.168.92.77", "ntp server 192.168.0.5"])
    print ("Router Done!")

# Note: You must have SSH connection to the devices if you are willing to use Netmiko.