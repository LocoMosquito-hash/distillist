# backend/app/security.py


from cryptography.fernet import Fernet
from itsdangerous import BadSignature, TimestampSigner

from app.config import Settings

_SESSION_SALT: str = "distillist-session"


def _fernet(settings: Settings) -> Fernet:
    return Fernet(settings.token_encryption_key.get_secret_value().encode())


def encrypt_token(settings: Settings, plaintext: str) -> str:
    """Encrypt a Spotify token before it is written to the database."""
    return _fernet(settings).encrypt(plaintext.encode()).decode()


def decrypt_token(settings: Settings, ciphertext: str) -> str:
    """Decrypt a token read from the database."""
    return _fernet(settings).decrypt(ciphertext.encode()).decode()


def _signer(settings: Settings) -> TimestampSigner:
    return TimestampSigner(
        settings.session_secret_key.get_secret_value(),
        salt=_SESSION_SALT,
    )


def sign_session_id(settings: Settings, session_id: str) -> str:
    """Return the tamper-proof value stored in the browser's session cookie."""
    return _signer(settings).sign(session_id).decode()


def unsign_session_id(settings: Settings, signed_value: str) -> str | None:
    """Return the session id inside a cookie value, or None if it is forged/expired."""
    try:
        return _signer(settings).unsign(
            signed_value, max_age=settings.session_ttl_seconds
        ).decode()
    except BadSignature:  # also covers SignatureExpired
        return None
