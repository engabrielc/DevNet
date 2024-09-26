import re
import csv

def extract_vip_info(file_path, output_csv):
    with open(file_path, 'r') as file:
        data = file.read()

    vip_blocks = re.findall(r"'vsvip': \{(.*?)\},", data, re.DOTALL)
    rows = []

    for block in vip_blocks:
        try:
            name = re.search(r"'name':\s*'([^']+)'", block).group(1)
            ip = re.search(r"'addr':\s*'([^']+)'", block).group(1)
            rows.append([name, ip])
        except AttributeError:
            print("Could not extract name or IP.")

    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['VIP Name', 'IP Address'])
        writer.writerows(rows)

file_path = 'path_to_your_text_file.txt'
output_csv = 'output_vips.csv'
extract_vip_info(file_path, output_csv)
