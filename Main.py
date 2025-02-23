import os
import re
import socket
import requests
from bs4 import BeautifulSoup
from colorama import init

init(autoreset=True)  # Initialize colorama for automatic resetting of colors after each print

ICON_FOLDER = "icons"  # Folder where the .png files are stored

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
        return "No matching icon found"

    title_cleaned = title.lower().replace("communications", "").strip()  # Remove unnecessary words
    title_words = title_cleaned.split()

    # Check if an exact match PNG exists
    for filename in os.listdir(ICON_FOLDER):
        if filename.lower() == f"{title_cleaned}.png":
            return os.path.join(ICON_FOLDER, filename)

    # Check if a PNG exists for any word in the title
    for word in title_words:
        possible_filename = f"{word}.png"
        if possible_filename in os.listdir(ICON_FOLDER):
            return os.path.join(ICON_FOLDER, possible_filename)

    return "No matching icon found"

def display_device_info(ip):
    title = get_webpage_title(ip)
    icon_path = find_matching_icon(title)

    print(f"IP: {ip} - Title: {title} - Icon: {icon_path}")

input_ips = input("Enter IPs (can contain junk data): ").split(',')
ips = extract_ips(input_ips)

proceed = input("Do you want to check ports for these IPs? (yes/no): ").strip().lower()

if proceed == 'yes':
    print("IP addresses will be printed at the end.")

    ports, timeout = get_input()
    successful_connections = check_ports(ips, ports, timeout)

    for ip, open_ports in successful_connections.items():
        if open_ports:
            print(f"IP {ip} has open ports: {', '.join(map(str, open_ports))}")
        else:
            print(f"IP {ip} has no open ports.")

    print("\n" * 2)

    for ip in ips:
        display_device_info(ip)

    print("z")
else:
    print("Here are the IPs you entered:")
    for ip in ips:
        print(f"IP: {ip}")
    print("bye bye!")
