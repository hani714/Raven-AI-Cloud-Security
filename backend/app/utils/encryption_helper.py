from cryptography.fernet import Fernet, InvalidToken
from app.utils import settings


def _get_fernet() -> Fernet:
    key = settings.ENCRYPTION_KEY
    if not key:
        raise ValueError("ENCRYPTION_KEY is not set in environment.")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_api_key(api_key: str) -> str:
    f = _get_fernet()
    return f.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    try:
        f = _get_fernet()
        return f.decrypt(encrypted_key.encode()).decode()
    except InvalidToken:
        raise ValueError("Failed to decrypt API key — key may be corrupted or tampered with.")