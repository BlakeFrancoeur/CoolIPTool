import os
import re
import socket
import requests
from bs4 import BeautifulSoup

ICON_FOLDER = "icons"  # Folder where the .png files are stored
HTML_FILE = "scan_results.html"  # Output HTML file

def extract_ips(ip_list):
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    return re.findall(ip_pattern, ",".join(ip_list))

def get_input():
    ports = input("Enter port numbers separated by commas (e.g., 23, 3445): ")
    timeout = input("Enter timeout duration in seconds (e.g., 7): ")

    try:
        timeout = int(timeout)
    except ValueError:
        print("Invalid timeout value, setting to 7 seconds.")
        timeout = 7

    return [port.strip() for port in ports.split(',')], timeout

def check_ports(ip_list, port_list, timeout):
    successful_connections = {}

    for ip in ip_list:
        successful_connections[ip] = []
        for port in port_list:
            try:
                sock = socket.create_connection((ip, int(port)), timeout=timeout)
                successful_connections[ip].append(port)
                sock.close()
            except (socket.timeout, socket.error):
                continue  # Move to the next port if connection is denied

    return successful_connections

def get_webpage_title(ip):
    try:
        url = f"http://{ip}"
        response = requests.get(url, timeout=7)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string.strip() if soup.title else "No Title Found"
            return title
        else:
            return "No Title Found"
    
    except (requests.RequestException, AttributeError):
        return "No Title Found"

def find_matching_icon(title):
    if title == "No Title Found":
        return None

    title_cleaned = title.lower().replace("communications", "").strip()
    title_words = title_cleaned.split()

    # Exact match
    for filename in os.listdir(ICON_FOLDER):
        if filename.lower() == f"{title_cleaned}.png":
            return os.path.join(ICON_FOLDER, filename)

    # Check for any word match
    for word in title_words:
        possible_filename = f"{word}.png"
        if possible_filename in os.listdir(ICON_FOLDER):
            return os.path.join(ICON_FOLDER, possible_filename)

    return None

def generate_html_report(results):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Port Scan Results</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            img { max-width: 50px; max-height: 50px; }
        </style>
    </head>
    <body>
        <h2>Port Scan Results</h2>
        <table>
            <tr>
                <th>IP Address</th>
                <th>Title</th>
                <th>Open Ports</th>
                <th>Icon</th>
            </tr>
    """

    for ip, data in results.items():
        title = data["title"]
        ports = ", ".join(map(str, data["ports"])) if data["ports"] else "None"
        icon_path = data["icon"]
        icon_html = f'<img src="{icon_path}" alt="Icon">' if icon_path else "No Icon"

        html_content += f"""
            <tr>
                <td>{ip}</td>
                <td>{title}</td>
                <td>{ports}</td>
                <td>{icon_html}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(HTML_FILE, "w") as file:
        file.write(html_content)

    print(f"HTML report generated: {HTML_FILE}")

input_ips = input("Enter IPs (can contain junk data): ").split(',')
ips = extract_ips(input_ips)

proceed = input("Do you want to check ports for these IPs? (yes/no): ").strip().lower()

results = {}

if proceed == 'yes':
    print("Scanning ports... IP addresses will be printed at the end.")

    ports, timeout = get_input()
    successful_connections = check_ports(ips, ports, timeout)

    for ip in ips:
        title = get_webpage_title(ip)
        icon_path = find_matching_icon(title)

        results[ip] = {
            "title": title,
            "ports": successful_connections.get(ip, []),
            "icon": icon_path
        }

    generate_html_report(results)

else:
    print("Here are the IPs you entered:")
    for ip in ips:
        print(f"IP: {ip}")
    print("bye bye!")
