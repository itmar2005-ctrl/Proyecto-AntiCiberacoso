import os
import base64
import json
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class CryptoEngine:
    def __init__(self, key: Optional[bytes] = None):
        self._key = key or self._load_or_create_key()
        self._fernet = Fernet(base64.urlsafe_b64encode(self._key[:32]))

    @staticmethod
    def _load_or_create_key() -> bytes:
        key_path = os.path.expanduser("~/.purple_team_key")
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                return f.read()
        key = AESGCM.generate_key(bit_length=256)
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        with open(key_path, "wb") as f:
            f.write(key)
        os.chmod(key_path, 0o600)
        return key

    def encrypt(self, data: bytes) -> bytes:
        return self._fernet.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        return self._fernet.decrypt(data)

    @staticmethod
    def encrypt_aes_gcm(key: bytes, data: bytes) -> Tuple[bytes, bytes]:
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, data, None)
        return nonce, ct

    @staticmethod
    def decrypt_aes_gcm(key: bytes, nonce: bytes, ct: bytes) -> bytes:
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ct, None)

    def encrypt_dict(self, data: dict) -> str:
        payload = json.dumps(data, separators=(",", ":")).encode()
        encrypted = self.encrypt(payload)
        return base64.b64encode(encrypted).decode()

    def decrypt_dict(self, data: str) -> dict:
        decoded = base64.b64decode(data)
        decrypted = self.decrypt(decoded)
        return json.loads(decrypted)

    @staticmethod
    def generate_keypair() -> Tuple[bytes, bytes]:
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        return (
            private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            ),
            public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ),
        )

    @staticmethod
    def derive_shared_key(private: bytes, public: bytes) -> bytes:
        priv_key = x25519.X25519PrivateKey.from_private_bytes(private)
        pub_key = x25519.X25519PublicKey.from_public_bytes(public)
        shared_secret = priv_key.exchange(pub_key)
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"purple-team-key-exchange",
        ).derive(shared_secret)

    def encrypt_payload(self, payload: dict, peer_public_key: Optional[bytes] = None) -> dict:
        if peer_public_key:
            priv, pub = self.generate_keypair()
            shared = self.derive_shared_key(priv, peer_public_key)
            nonce, ct = self.encrypt_aes_gcm(
                shared, json.dumps(payload).encode()
            )
            return {
                "ephemeral_key": base64.b64encode(pub).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "ciphertext": base64.b64encode(ct).decode(),
            }
        return {
            "ciphertext": self.encrypt_dict(payload),
        }

    def decrypt_payload(self, payload: dict, peer_public_key: Optional[bytes] = None) -> dict:
        if peer_public_key and "ephemeral_key" in payload:
            eph_key = base64.b64decode(payload["ephemeral_key"])
            nonce = base64.b64decode(payload["nonce"])
            ct = base64.b64decode(payload["ciphertext"])
            shared = self.derive_shared_key(self._key[:32], eph_key)
            data = self.decrypt_aes_gcm(shared, nonce, ct)
            return json.loads(data)
        return self.decrypt_dict(payload["ciphertext"])


crypto = CryptoEngine()
