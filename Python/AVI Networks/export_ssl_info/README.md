
# AVI Controller SSL Certificate Fetch Script

This script authenticates with an AVI Controller, retrieves all tenant UUIDs, and then collects SSL certificates for each tenant. The SSL certificate data is saved in individual JSON files for each tenant, with each file containing unfiltered, paginated API responses.

## Prerequisites

- Python 3.x
- `requests` library (Install via `pip install requests` if not already installed)

## Usage

1. Clone or download the script.
2. Place the script in your preferred directory.
3. Run the script from the command line:
   ```bash
   python script_name.py
   ```

## Script Structure

### 1. Authentication

The script first authenticates with the AVI Controller by sending a POST request with the username and password to the `/login` endpoint. It captures the session and CSRF tokens for subsequent requests.

### 2. Retrieving Tenants

The script retrieves all tenants' UUIDs from the AVI Controller using a paginated GET request to the `/api/tenant` endpoint. The results are stored in a dictionary with tenant names as keys and UUIDs as values. The "admin" tenant is included with "admin" as its UUID by default.

### 3. Fetching SSL Certificates

For each tenant, the script requests SSL certificates from a tenant-specific API endpoint (`/api/tenant/{tenant_uuid}/sslkeyandcertificate/?export_key=true`). This is a paginated request, so it continues fetching until all pages are retrieved.

### 4. Saving Data

Each tenant's SSL certificate data is saved as a separate JSON file in the `tenant_certificates` directory. The filenames are formatted as `{tenant_name}_ssl_certificates.json`.

## Example Output

After running the script, you will find the `tenant_certificates` directory containing JSON files for each tenant. Each file contains the unmodified SSL certificate data in JSON format.

## Troubleshooting

- Ensure that your AVI Controller IP, username, and password are correct.
- Verify network connectivity to the AVI Controller.
- If you encounter `SSL certificate verification` issues, the script disables SSL warnings, but ensure security compliance.

## Important Notes

- The script saves sensitive certificate and key data; handle these files securely.
- The script handles both authentication and pagination automatically, so no further configuration is required.

## License

This script is provided "as-is" without warranty of any kind.
