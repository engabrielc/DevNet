# Prompt user for VLAN IDs
vlan_input = input("Enter VLAN IDs separated by commas (e.g., 12,20,21,...): ")

# Convert input string to a list of integers
vlan_ids = [int(v.strip()) for v in vlan_input.split(",") if v.strip().isdigit()]

# Print the full VLAN list
print(f"vlan {vlan_input}\n")

# 1. Print VLANs and vn-segments
for vlan_id in vlan_ids:
    vni = f"10{vlan_id}"
    print(f"vlan {vlan_id}")
    print(f"    vn-segment {vni}")
    print()

# 2. Print interface nve1 once, and then each member vni
print("interface nve1\n")
for vlan_id in vlan_ids:
    vni = f"10{vlan_id}"
    print(f"  member vni {vni}")
    print("    ingress-replication protocol static")
    print("      peer-ip 10.21.0.50")
    print()


