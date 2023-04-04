import CloudFlare

def main():
    zone_name = input("Insert zone: ")
    confirmation = input(f'Are you sure you want to delete "{zone_name}" ? (Type yes or no) ')
    if confirmation.lower() != "yes":
        exit()
    try:
        token = 'xxx'
        cf = CloudFlare.CloudFlare(token=token)
        zone_info = cf.zones.get(params={'name': zone_name})
        if len(zone_info) == 0:
            print(f'Zone "{zone_name}" does not exist.')
        else:
            zone_id = zone_info[0]['id']
            delete = cf.zones.delete(zone_id)
            print(f'{zone_name} has been deleted.')
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        print(f'Error deleting {zone_name}: {e}')

if __name__ == '__main__':
    main()
