from cryptography.fernet import Fernet
import os

# Generate a key once and store it in env or generate dynamically if not exists
# In production, this should be a stable key stored safely.
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()

def decrypt(encrypted_text: str) -> str:
    return cipher.decrypt(encrypted_text.encode()).decode()
