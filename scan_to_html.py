import os
import re
import socket
import requests
from bs4 import BeautifulSoup

ICON_FOLDER = "icons"  # Folder where the .png files are stored
HTML_FILE = "scan_results.html"  # Output HTML file

# Check and delete old scan_results.html before proceeding
if os.path.exists(HTML_FILE):
    os.remove(HTML_FILE)
    print(f"Deleted old {HTML_FILE}, starting fresh...")

# Maximum number of rows (50 in this case)
MAX_ROWS = 50

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

    # Check for an exact match
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
    """Generates an HTML report with only the valid results."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Port Scan Results</title>
        <link rel="stylesheet" href="style.css">  <!-- Link to external CSS -->
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

    # Only add rows for the actual IPs in the results list
    if not results:
        html_content += "<tr><td colspan='4'>No results found</td></tr>"
    else:
        for result in results:
            ip = result["ip"]
            title = result["title"]
            ports = ", ".join(map(str, result["ports"])) if result["ports"] else "None"
            icon_path = result["icon"]
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

    with open(HTML_FILE, "w") as file:  # Always overwrite with new results
        file.write(html_content)

    print(f"Updated HTML report: {HTML_FILE}")

# Main script execution
input_ips = input("Enter IPs (can contain junk data): ").split(',')
ips = extract_ips(input_ips)

proceed = input("Do you want to check ports for these IPs? (yes/no): ").strip().lower()

results = []

if proceed == 'yes':
    print("Scanning ports... IP addresses will be printed at the end.")

    ports, timeout = get_input()
    successful_connections = check_ports(ips, ports, timeout)

    for ip in ips:
        title = get_webpage_title(ip)
        icon_path = find_matching_icon(title)

        results.append({
            "ip": ip,
            "title": title,
            "ports": successful_connections.get(ip, []),
            "icon": icon_path
        })

    generate_html_report(results)

else:
    print("Here are the IPs you entered:")
    for ip in ips:
        print(f"IP: {ip}")
    print("bye bye!")
