from cloudflare import Cloudflare

# Step 1: Prompt user for email and API token
email = input("Enter your Cloudflare email: ")
api_token = input("Enter your Cloudflare API token: ")

# Initialize the Cloudflare client
client = Cloudflare(
    api_email=email,
    api_key=api_token
)

# Step 2: List all the zones
zones = client.zones.list()

# Step 3: Prompt user to enter the Zone Name they are looking for
zone_name = input("Enter the Zone Name you want to delete: ")

# Step 4: Ask for confirmation before deleting the zone
confirmation = input(f"Are you sure you want to delete the zone '{zone_name}'? Type 'yes' to confirm: ")

if confirmation.lower() == 'yes':
    # Search for the zone by name
    zone_found = None
    for zone in zones:
        if zone.name == zone_name:
            zone_found = zone
            break

    # Step 5: If zone found, delete it
    if zone_found:
        try:
            # Correctly delete the zone by passing the zone ID as a keyword argument
            client.zones.delete(zone_id=zone_found.id)
            print(f"Zone '{zone_name}' with ID '{zone_found.id}' has been successfully deleted.")
        except Exception as e:
            print(f"Error occurred while deleting the zone: {e}")
    else:
        print(f"No zone found with name '{zone_name}'")
else:
    print("Zone deletion was canceled.")
