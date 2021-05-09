import os
from cryptography.fernet import Fernet


def encrypt_password(password: str, key):
    f = Fernet(key)
    return str(f.encrypt(bytes(password, 'utf-8')), 'utf-8')


def decrypt_password(password: str, key):
    f = Fernet(key)
    return str(f.decrypt(bytes(password, 'utf-8')), 'utf-8')


KEY = os.environ.get("DASH_APP_KEY")