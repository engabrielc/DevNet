import requests
requests.packages.urllib3.disable_warnings()

# Login and capture the session
login = requests.post(
    'https://10.1.1.1/login', 
    verify=False, 
    data={'username': 'USER', 'password': 'PASSWORD'}
)

# Extract and print the session ID from cookies
session_id = login.cookies.get('sessionid')
print("Session ID:", session_id)

# Use the session ID in the next request
resp = requests.get(
    'https://10.1.1.1/api/cluster/version', 
    verify=False, 
    cookies={'sessionid': session_id}
)

# Logout
logout = requests.post(
    'https://10.1.1.1/logout', 
    verify=False, 
    headers={'X-CSRFToken': login.cookies.get('csrftoken'), 'Referer': 'https://10.1.1.1'}, 
    cookies=login.cookies
)


