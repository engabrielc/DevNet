
# DNS A Record Extraction Script

## Overview

This script extracts DNS A records from an EfficientIP DNS server via its REST API. It retrieves only forward zones (non-reverse) of type master and outputs the A records to a JSON file.

## Features

Filters DNS zones to include only:
- Forward zones (`dnszone_is_reverse='0'`)
- Master zones (`dnszone_type='master'`)
- Uses pagination for large datasets
- Runs concurrently for faster data retrieval
- Saves only zones that contain A records
- Outputs data in a structured JSON file

## Requirements

- Python 3
- requests module

Install dependencies if needed:

```bash
pip install requests
```

## Configuration

Update the following in the script:
- `BASE_URL = "https://EfficientIP-Server/rest"`
- `USERNAME = "your_username"`
- `PASSWORD = "your_password"`

Replace `your_username` and `your_password` with your EfficientIP credentials.

## Output Format

The script generates a JSON file (`dns_A_records.json`) with the following structure:

```json
{
    "dns-server-1": {
        "example.com": [
            {"name": "www.example.com", "value": "192.168.1.10"},
            {"name": "mail.example.com", "value": "192.168.1.20"}
        ],
        "network.local": [
            {"name": "vpn.network.local", "value": "10.1.1.1"}
        ]
    }
}
```

Only zones with A records are included in the output.

## Running the Script

Run the script using:

```bash
python script.py
```

Once completed, the output will be saved in `dns_A_records.json`.

## Notes

- Ensure the EfficientIP API is accessible.
- Modify SSL verification settings (`VERIFY_SSL = False`) based on your environment.
- Uses multi-threading for better performance.

## License

This script is provided as-is for internal use. Modify it as needed for your environment.
