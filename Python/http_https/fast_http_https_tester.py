import requests
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress SSL warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def load_ips(filename):
    """Read IP addresses from a text file."""
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def test_http_https(ip, timeout=10, retries=2):
    """Perform HTTP and HTTPS tests on a given IP with retries."""
    results = [f"Results for {ip}:"]
    
    # Test HTTP
    http_url = f"http://{ip}"
    for attempt in range(retries + 1):
        try:
            response = requests.get(http_url, timeout=timeout)
            results.append(f"  HTTP - Status: {response.status_code}")
            break  # Success, so break out of retry loop
        except requests.RequestException as e:
            if attempt == retries:
                results.append(f"  HTTP - Failed after {retries + 1} attempts: {e}")

    # Test HTTPS
    https_url = f"https://{ip}"
    for attempt in range(retries + 1):
        try:
            response = requests.get(https_url, timeout=timeout, verify=False)
            results.append(f"  HTTPS - Status: {response.status_code}")
            break  # Success, so break out of retry loop
        except requests.RequestException as e:
            if attempt == retries:
                results.append(f"  HTTPS - Failed after {retries + 1} attempts: {e}")
    
    return "\n".join(results)

def log_to_file(filename, messages):
    """Log messages to a file in batches."""
    with open(filename, 'a') as file:
        for message in messages:
            file.write(message + '\n')

def main(input_file, output_file):
    ips = load_ips(input_file)
    batch_size = 10  # Number of IPs to process per batch for file writing
    results = []
    
    # Use ThreadPoolExecutor for concurrency
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(test_http_https, ip): ip for ip in ips}
        
        # Collect results as they complete
        for count, future in enumerate(as_completed(futures), start=1):
            ip = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Processed {count}/{len(ips)} IPs: {ip}")
            except Exception as e:
                print(f"Error processing {ip}: {e}")
            
            # Write to file in batches
            if len(results) >= batch_size:
                log_to_file(output_file, results)
                results.clear()
    
    # Log any remaining results
    if results:
        log_to_file(output_file, results)

if __name__ == "__main__":
    input_file = "ips.txt"  # Input file with IP addresses
    output_file = "scan_results.txt"  # Output file for results
    main(input_file, output_file)

