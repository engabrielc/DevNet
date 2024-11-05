
# Combined NSLookup and FQDN Export Script

## Overview

The `nslookup_and_export_fqdns.py` script performs an `nslookup` on a list of IP addresses provided in a text file (`ips.txt`) to retrieve PTR records (reverse DNS). The script saves the complete `nslookup` results to a file (`nslookup_results.txt`) and extracts only the successful FQDNs (hostnames) to a separate file (`fqdns.txt`).

This script is optimized to handle large lists of IPs concurrently and includes retry logic for reliability.

## Features

- **NSLookup for IPs**: Attempts a reverse DNS lookup on each IP to retrieve the hostname.
- **Retry Logic**: Automatically retries failed lookups a few times to handle potential network delays.
- **Concurrent Processing**: Uses Python’s `ThreadPoolExecutor` to process multiple IPs concurrently for faster execution.
- **Export of FQDNs**: Extracts only the fully qualified domain names (FQDNs) from successful lookups to a separate file.
- **Batch Logging**: Logs results in batches for better performance.

## Requirements

- **Python 3.6+**: This script uses the built-in `socket` and `concurrent.futures` libraries.

## Script Structure and Key Functions

### 1. `load_ips(filename)`

- **Purpose**: Reads a list of IP addresses from a specified file.
- **Parameters**: 
  - `filename` (str): The path to the text file containing IP addresses (one per line).
- **Returns**: A list of IP addresses as strings.

### 2. `perform_nslookup(ip, retries=2, delay=1)`

- **Purpose**: Performs a reverse DNS lookup on a given IP address with retry logic.
- **Parameters**:
  - `ip` (str): The IP address to perform `nslookup` on.
  - `retries` (int): The number of retries for each IP lookup (default is 2).
  - `delay` (int): Delay in seconds between retries (default is 1 second).
- **Returns**: A string with the IP and hostname if successful, or a message indicating no PTR record or an error.

### 3. `log_to_file(filename, messages)`

- **Purpose**: Logs messages to a file in batches to reduce I/O operations.
- **Parameters**:
  - `filename` (str): The path to the output file.
  - `messages` (list): A list of strings to log to the file.
  
### 4. `extract_fqdns(nslookup_file, fqdn_file)`

- **Purpose**: Reads the full `nslookup` results and extracts only the FQDNs for successful lookups.
- **Parameters**:
  - `nslookup_file` (str): The file with full `nslookup` results.
  - `fqdn_file` (str): The file where extracted FQDNs will be saved.

### 5. `main(input_file, nslookup_output_file, fqdn_output_file)`

- **Purpose**: The main function that performs `nslookup`, logs results, and extracts FQDNs.
- **Parameters**:
  - `input_file` (str): Path to the file containing IP addresses.
  - `nslookup_output_file` (str): Path to the output file for full `nslookup` results.
  - `fqdn_output_file` (str): Path to the output file for extracted FQDNs.

## Usage

1. Prepare an input file (`ips.txt`) with IP addresses, each on a new line.
2. Run the script:
   ```bash
   python nslookup_and_export_fqdns.py
   ```
3. Check the output files:
   - **`nslookup_results.txt`**: Contains the full `nslookup` results with IPs and their PTR records (or "No PTR record found").
   - **`fqdns.txt`**: Contains only the FQDNs (hostnames) for successful lookups, one per line.

### Sample Output in `fqdns.txt`

For IPs with successful reverse DNS lookups, the output file will contain lines like:

```plaintext
example-host.example.com
dns.google
another-host.example.net
```

Only IPs with PTR records will be included in `fqdns.txt`, making it a clean list of resolved hostnames.
