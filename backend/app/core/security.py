"""
Security and JWT token generation/validation utilities.
Uses HMAC-SHA256 for standard JWT encoding/decoding without requiring compiled C extensions.
"""
import base64
import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional
from backend.app.config import settings


def hash_password(password: str) -> str:
    """
    Hashes a password with a SHA-256 salt.
    """
    salt = settings.SECRET_KEY[:16]
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the stored hash.
    """
    return hash_password(plain_password) == hashed_password


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def base64url_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding < 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("utf-8"))


def create_access_token(data: Dict[str, Any], expires_delta_seconds: Optional[int] = None) -> str:
    """
    Generates a standard signed JWT token.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    now = int(time.time())
    exp = now + (expires_delta_seconds or (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60))
    payload["iat"] = now
    payload["exp"] = exp

    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    unsigned_token = f"{base64url_encode(header_bytes)}.{base64url_encode(payload_bytes)}"
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        unsigned_token.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return f"{unsigned_token}.{base64url_encode(signature)}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validates signature and expiration, returns the payload dict or None.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts
        unsigned_token = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            unsigned_token.encode("utf-8"),
            hashlib.sha256
        ).digest()

        if not hmac.compare_digest(base64url_encode(expected_sig), sig_b64):
            return None

        payload_bytes = base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify expiration
        if "exp" in payload and int(time.time()) > payload["exp"]:
            return None

        return payload
    except Exception:
        return None
