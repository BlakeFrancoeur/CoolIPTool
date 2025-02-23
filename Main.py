import os
import re
import socket
import requests
from bs4 import BeautifulSoup
from PIL import Image
from colorama import init

init(autoreset=True)  

ICON_FOLDER = "icons"  

def extract_ips(ip_list):
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    return re.findall(ip_pattern, ",".join(ip_list))

def get_webpage_title(ip):
    try:
        url = f"http://{ip}"
        response = requests.get(url, timeout=7)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.title.string.strip() if soup.title else "No Title Found"
    
    except (requests.RequestException, AttributeError):
        pass
    
    return "No Title Found"

def find_matching_icon(title):
    if title == "No Title Found":
        return None  

    title_cleaned = title.lower().replace("communications", "").strip()  
    title_words = title_cleaned.split()

    for filename in os.listdir(ICON_FOLDER):
        if filename.lower() == f"{title_cleaned}.png":
            return os.path.join(ICON_FOLDER, filename)

    for word in title_words:
        possible_filename = f"{word}.png"
        if possible_filename in os.listdir(ICON_FOLDER):
            return os.path.join(ICON_FOLDER, possible_filename)

    return None  

def display_device_info(ip):
    title = get_webpage_title(ip)
    icon_path = find_matching_icon(title)

    print(f"IP: {ip} - Title: {title}")

    if icon_path:
        print(f"Opening image: {icon_path}")
        img = Image.open(icon_path)
        img.show()  
    else:
        print("No matching icon found.")

input_ips = input("Enter IPs: ").split(',')
ips = extract_ips(input_ips)

for ip in ips:
    display_device_info(ip)
