"""Password hashing utilities for the A2A Agent Registry."""

import secrets
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with SHA-256."""

    salt = secrets.token_bytes(32)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode("utf-8"))
    return f"{salt.hex()}:{key.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a PBKDF2 hash."""

    try:
        salt_hex, key_hex = hashed_password.split(":", 1)
    except ValueError:
        return False

    if not salt_hex or not key_hex:
        return False

    try:
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
    except ValueError:
        return False

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )

    try:
        kdf.verify(password.encode("utf-8"), key)
        return True
    except Exception:
        return False
