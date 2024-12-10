
# Cloudflare Zone Deletion Script

## Description
This script allows you to delete a zone from your Cloudflare account by providing the zone name. It prompts you for your Cloudflare email and API token, searches for the specified zone by name, and asks for confirmation before deleting it. If the zone is found and confirmed for deletion, the script proceeds to delete it.

## Prerequisites
- Python 3.x
- `cloudflare` Python package

## Installation
To use this script, you'll need to have Python installed and the Cloudflare Python package. If you haven't installed it yet, you can do so using pip:

```bash
pip install cloudflare
```

The Cloudflare Python SDK can be found on GitHub at [Cloudflare Python SDK](https://github.com/cloudflare/cloudflare-python).

## Usage
1. **Clone or download the script**.
2. Run the script:

```bash
python delete_zone.py
```

3. The script will prompt you to enter the following information:
    - **Your Cloudflare email**: The email associated with your Cloudflare account.
    - **Your Cloudflare API token**: The API token for authentication.
    - **Zone Name**: The name of the zone you want to delete.
    - **Confirmation**: Type `yes` to confirm that you want to delete the specified zone.

4. If the zone is found and successfully deleted, a success message will be displayed. If the zone is not found or any error occurs during deletion, the script will inform you accordingly.

## Example
```bash
Enter your Cloudflare email: example@example.com
Enter your Cloudflare API token: your-api-token
Enter the Zone Name you want to delete: example.com
Are you sure you want to delete the zone 'example.com'? Type 'yes' to confirm: yes
Zone 'example.com' with ID 'your-zone-id' has been successfully deleted.
```

## Error Handling
If an error occurs during zone deletion, an error message will be shown.

## License
This project is licensed under the MIT License.

