"""
Fernet symmetric encryption for API credentials.
Key stored in .env as ENCRYPTION_KEY.
"""
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

_KEY = os.getenv("ENCRYPTION_KEY")


def _get_fernet():
    if not _KEY:
        raise ValueError("ENCRYPTION_KEY not set in .env. Generate one with: "
                         "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
    return Fernet(_KEY.encode())


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string, return base64-encoded ciphertext."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    """Decrypt a base64-encoded ciphertext back to string."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()


def generate_key() -> str:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key().decode()
