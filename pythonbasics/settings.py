import os
import dj_database_url
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Retry Settings
MAX_RETRIES = 5  # Retry 5 times before failing
SLEEP_BETWEEN_RETRIES = 5  # Wait 5 seconds between retries

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-secret-key")

DEBUG = False  # Change to True only for local debugging

ALLOWED_HOSTS = ["https://python-basics.onrender.com", "localhost"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Whitenoise for serving static files in production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Enable static file serving
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Ensure Django can find templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Retrieve DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    try:
        # Extract the hostname from DATABASE_URL (format: postgres://user:pass@hostname:port/dbname)
        hostname = DATABASE_URL.split('@')[1].split(':')[0]  # Extracts "dpg-cv8usiq3esus73fhij20-a"
        logging.info(f"Extracted database hostname: {hostname}")

        # Resolve the IP address
        ip_address = socket.gethostbyname(hostname)
        logging.info(f"Resolved {hostname} to IP: {ip_address}")

        # Override the database hostname with the resolved IP
        DATABASE_URL = DATABASE_URL.replace(hostname, ip_address)
        logging.info(f"Updated DATABASE_URL with IP: {DATABASE_URL}")

    except Exception as e:
        logging.warning(f"Failed to resolve hostname: {e}")

# Define DATABASES in Django settings
DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
