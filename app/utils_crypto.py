import base64
import binascii
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import pyotp


def generate_rsa_keypair(private_path="student_private.pem", public_path="student_public.pem", key_size=4096):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(private_path, "wb") as f:
        f.write(priv_pem)

    pub_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(public_path, "wb") as f:
        f.write(pub_pem)

    return private_key, private_key.public_key()


def load_private_key(path="student_private.pem"):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_private_key(data, password=None, backend=default_backend())


def load_public_key(path="student_public.pem"):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_public_key(data, backend=default_backend())


def decrypt_seed(encrypted_seed_b64: str, private_key):
    try:
        ct = base64.b64decode(encrypted_seed_b64)
    except Exception as e:
        raise ValueError("Base64 decode failed") from e

    plaintext = private_key.decrypt(
        ct,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    try:
        hex_seed = plaintext.decode("utf-8").strip()
    except Exception as e:
        raise ValueError("Decrypted seed not utf-8") from e

    if len(hex_seed) != 64:
        raise ValueError("Decrypted seed length is not 64 characters")

    if not all(c in "0123456789abcdef" for c in hex_seed):
        raise ValueError("Decrypted seed contains invalid characters")

    return hex_seed


def hex_to_base32(hex_seed: str) -> str:
    bs = bytes.fromhex(hex_seed)
    b32 = base64.b32encode(bs).decode("utf-8")
    return b32


def generate_totp_code(hex_seed: str) -> str:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    return totp.verify(code, valid_window=valid_window)


def sign_message_rsa_pss(message: str, private_key):
    signature = private_key.sign(
        message.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def encrypt_with_public_key(data: bytes, public_key):
    ct = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ct