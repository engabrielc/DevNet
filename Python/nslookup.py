import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_ips(filename):
    """Read IP addresses from a text file."""
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def perform_nslookup(ip, retries=2, delay=1):
    """Perform an nslookup for the given IP address with retries."""
    for attempt in range(retries + 1):
        try:
            # Perform reverse DNS lookup
            hostname = socket.gethostbyaddr(ip)[0]
            return f"{ip} - Hostname: {hostname}"
        except socket.herror:
            if attempt == retries:
                return f"{ip} - No PTR record found"  # Final attempt, return no PTR record
            else:
                time.sleep(delay)  # Wait before retrying
        except Exception as e:
            return f"{ip} - Error: {e}"

def log_to_file(filename, messages):
    """Log messages to a file in batches."""
    with open(filename, 'a') as file:
        for message in messages:
            file.write(message + '\n')

def main(input_file, output_file):
    ips = load_ips(input_file)
    results = []
    batch_size = 10  # Number of results to write in each batch for efficiency
    
    # Use ThreadPoolExecutor for concurrent nslookup processing
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(perform_nslookup, ip): ip for ip in ips}
        
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
    output_file = "nslookup_results.txt"  # Output file for results
    main(input_file, output_file)
