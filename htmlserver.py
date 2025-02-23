import os
import http.server
import socketserver
import time
import shutil

def host_html():
    # Define the handler and port
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler

    # Check if the HTML file exists and move it to the 'html' folder
    if os.path.exists("scan_results.html"):
        # Create 'html' folder if it doesn't exist
        if not os.path.exists("html"):
            os.mkdir("html")

        # Move the HTML file to the 'html' folder
        shutil.move("scan_results.html", os.path.join("html", "scan_results.html"))
        print("Moved scan_results.html to the 'html' folder.")

        # Start the server to serve the file
        print(f"Hosting scan_results.html at http://localhost:8000/html/scan_results.html")
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving at port {PORT}")
            time.sleep(1)  # Allow time for the server to initialize
            httpd.serve_forever()
    else:
        print("OH NO ME BOYO! THERE'S NO HTML FILE! GO MAKE ME ONE, WILL YA BOYO?")

def delete_html():
    # Check if the file exists and delete it from the 'html' folder
    html_path = os.path.join("html", "scan_results.html")
    if os.path.exists(html_path):
        os.remove(html_path)
        print("scan_results.html has been deleted.")
    else:
        print("scan_results.html not found in the 'html' folder, nothing to delete.")

def main():
    # Ask user if they want to host the HTML file
    host_input = input("Host HTML file? (yes/no): ").strip().lower()

    if host_input == "yes":
        host_html()

        # After hosting, ask if they want to delete the HTML file
        delete_input = input("Do you want to delete the HTML file after hosting? (yes/no): ").strip().lower()

        if delete_input == "yes":
            delete_html()
        else:
            print("The HTML file was not deleted.")

    else:
        print("Exiting program.")

if __name__ == "__main__":
    main()
