import os

USERNAME = os.getenv("LOGIN_USERNAME", "admin")
PASSWORD = os.getenv("LOGIN_PASSWORD", "password")

def check_password(username, password):
    return username == USERNAME and password == PASSWORD
