
# vADC Virtual Server Exporter

This Python script queries multiple vADCs (Virtual Application Delivery Controllers) for their virtual server configurations and exports the results into an Excel file.

## Features
- Connects to a list of vADCs via HTTPS.
- Authenticates using username and password.
- Fetches virtual server information (`VirtServerIndex` and `VirtServerIpAddress`).
- Saves the data into an Excel workbook, with each vADC having its own sheet.

## Requirements
- Python 3.8+
- Required Python packages:
  - `requests`
  - `openpyxl`
  - `urllib3` (for disabling SSL warnings)

Install dependencies via pip:

```bash
pip install requests openpyxl urllib3
```

## Usage

1. Update the `vadcs` dictionary with your vADC names and IP addresses:

```python
vadcs = {
    "Name_on_the_Sheet_vADC_1": "X.X.X.X",
    "Name_on_the_Sheet_vADC_2": "Z.Z.Z.Z"
}
```

2. Run the script:

```bash
python export_vadcs.py
```

3. Enter your credentials when prompted.

4. Upon successful execution, an Excel file `virtual_servers_all_vadcs.xlsx` will be generated, containing one sheet per vADC with virtual server information.

## Notes
- SSL verification is disabled (`verify=False`) for convenience. Use with caution in production environments.
- Failed queries or authentication issues will be printed to the console.

## Example Output

| VirtServerIndex | VirtServerIpAddress |
|-----------------|------------------|
| 1               | 10.0.0.1         |
| 2               | 10.0.0.2         |

Each vADC will have its own sheet in the Excel workbook.

## License
This project is open-source and free to use.
