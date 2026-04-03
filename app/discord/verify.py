from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


def verify_discord_signature(public_key_hex: str, signature_hex: str, timestamp: str, body: bytes) -> bool:
    verify_key = VerifyKey(bytes.fromhex(public_key_hex))
    message = timestamp.encode("utf-8") + body
    try:
        verify_key.verify(message, bytes.fromhex(signature_hex))
        return True
    except (BadSignatureError, ValueError):
        return False
