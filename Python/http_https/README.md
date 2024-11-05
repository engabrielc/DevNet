
# Fast HTTP/HTTPS Tester Script

## Overview

The `fast_http_https_tester.py` script performs HTTP and HTTPS connection tests on a list of IP addresses provided in a text file (`ips.txt`). For each IP, the script attempts both HTTP (`http://<ip>`) and HTTPS (`https://<ip>`) requests, records the status of each connection (including any errors), and saves the results to an output file (`scan_results.txt`). 

This script is optimized for speed and efficiency by using concurrent threads to test multiple IPs simultaneously, making it suitable for large lists of IPs.

## Features

- **HTTP and HTTPS Testing**: Attempts both HTTP and HTTPS connections for each IP.
- **Concurrent Execution**: Uses Python’s `ThreadPoolExecutor` to test multiple IPs at once, reducing runtime.
- **Connection Status Logging**: Logs successful status codes (e.g., 200 OK) as well as errors (e.g., timeouts, connection refusals).
- **SSL Verification Suppression**: Ignores SSL certificate errors for HTTPS, allowing connections to IPs with self-signed or invalid certificates.
- **Progress Tracking**: Prints progress updates to the console for real-time feedback on the script’s activity.

## Requirements

- **Python 3.6+**
- **Requests Library**: Install it with `pip`:
  ```bash
  pip install requests
  ```

## Script Structure and Key Functions

### 1. `load_ips(filename)`

- **Purpose**: Reads a list of IP addresses from a specified file.
- **Parameters**: 
  - `filename` (str): The path to the text file containing IP addresses (one per line).
- **Returns**: A list of IP addresses as strings.

### 2. `test_http_https(ip, timeout=3)`

- **Purpose**: Tests both HTTP and HTTPS connections for a given IP.
- **Parameters**:
  - `ip` (str): The IP address to test.
  - `timeout` (int): The timeout for each request in seconds (default is 3 seconds).
- **Returns**: A formatted string summarizing the HTTP and HTTPS connection results.

### 3. `log_to_file(filename, messages)`

- **Purpose**: Logs messages to a file in batches to reduce I/O operations.
- **Parameters**:
  - `filename` (str): The path to the output file.
  - `messages` (list): A list of strings to log to the file.
  
### 4. `main(input_file, output_file)`

- **Purpose**: The main function that loads IPs, performs HTTP and HTTPS tests, and logs the results.
- **Parameters**:
  - `input_file` (str): Path to the file containing IP addresses to test.
  - `output_file` (str): Path to the output file where results will be saved.
  
## Usage

1. Ensure you have the `requests` library installed by running:
   ```bash
   pip install requests
   ```

2. Prepare an input file (`ips.txt`) with IP addresses, each on a new line.

3. Run the script:
   ```bash
   python fast_http_https_tester.py
   ```

4. Check `scan_results.txt` for output. Each IP’s results will be grouped together, like this:
   ```plaintext
   Results for 151.138.251.11:
     HTTP - Status: 200
     HTTPS - Status: 200
   
   Results for 151.138.251.122:
     HTTP - Failed: Connection timed out
     HTTPS - Failed: Connection timed out
   ```
