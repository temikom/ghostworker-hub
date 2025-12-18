"""Encryption utilities for sensitive data at rest"""
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode
import hashlib
import os

from app.core.config import settings


def _get_encryption_key() -> bytes:
    """Derive encryption key from secret"""
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return urlsafe_b64encode(key)


_fernet = Fernet(_get_encryption_key())


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return data
    encrypted = _fernet.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return encrypted_data
    try:
        decrypted = _fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception:
        return encrypted_data  # Return as-is if decryption fails


def encrypt_credentials(credentials: dict) -> dict:
    """Encrypt sensitive fields in credentials dict"""
    sensitive_fields = ['access_token', 'refresh_token', 'api_key', 'secret', 'password', 'auth_token']
    encrypted = {}
    for key, value in credentials.items():
        if isinstance(value, str) and any(sf in key.lower() for sf in sensitive_fields):
            encrypted[key] = encrypt_data(value)
        else:
            encrypted[key] = value
    return encrypted


def decrypt_credentials(credentials: dict) -> dict:
    """Decrypt sensitive fields in credentials dict"""
    sensitive_fields = ['access_token', 'refresh_token', 'api_key', 'secret', 'password', 'auth_token']
    decrypted = {}
    for key, value in credentials.items():
        if isinstance(value, str) and any(sf in key.lower() for sf in sensitive_fields):
            decrypted[key] = decrypt_data(value)
        else:
            decrypted[key] = value
    return decrypted
