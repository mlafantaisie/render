import os
import socket
import dj_database_url

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    try:
        hostname = DATABASE_URL.split('@')[1].split(':')[0]  # Extract hostname
        print(f"Extracted hostname: {hostname}")

        ip_address = socket.gethostbyname(hostname)  # Resolve IP
        print(f"Resolved IP: {ip_address}")

    except Exception as e:
        print(f"❌ Failed to resolve IP: {e}")
else:
    print("❌ DATABASE_URL not found in environment variables.")
