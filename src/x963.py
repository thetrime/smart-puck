"""
Implements the X9.63 key derivation function with SHA-256
"""
import hashlib

def kdf(shared_secret: bytes, key_length: int, other_info: bytes = b''):
    """Implements ANSI X9.63 KDF with SHA-256"""
    key = b''
    counter = 1

    while len(key) < key_length:
        # Concatenate shared_secret + counter + otherInfo
        data = shared_secret + counter.to_bytes(4, "big") + other_info

        # Apply SHA-256
        key += hashlib.sha256(data).digest()

        counter += 1

    # the KDF allows us to specify how much of the data is actually needed
    return key[:key_length]
