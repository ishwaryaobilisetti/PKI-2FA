import base64
import time
import hmac
import hashlib
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


# -----------------------------
#  Load Keys
# -----------------------------
def load_private_key(path: str):
    """Load a PEM private key from file."""
    with open(path, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )


def load_public_key(path: str):
    """Load a PEM public key from file."""
    with open(path, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())


# -----------------------------
#  Decrypt Seed (API)
# -----------------------------
def decrypt_seed(encrypted_seed_b64: str) -> str:
    """Decrypt seed using student's private key inside container."""
    PRIVATE_KEY_PATH = "/app/student_private.pem"

    private_key = load_private_key(PRIVATE_KEY_PATH)
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    seed = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return seed.decode()


# -----------------------------
#  RSA-PSS SIGN (for prove_commit.py)
# -----------------------------
def sign_message_rsa_pss(private_key, message_bytes: bytes) -> str:
    """Sign message using RSA-PSS + SHA256, return Base64 string."""
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode()


# -----------------------------
#  RSA ENCRYPT WITH PUBLIC KEY
# -----------------------------
def encrypt_with_public_key(public_key, message: str) -> str:
    """Encrypt message using RSA-OAEP. Input is string → encrypt as bytes."""
    if isinstance(message, str):
        message = message.encode()   # <-- FIX ADDED HERE

    encrypted = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return base64.b64encode(encrypted).decode()


# -----------------------------
#  2FA GENERATION
# -----------------------------
def generate_2fa_code(seed: str) -> str:
    timestep = int(time.time() // 30)
    msg = f"{seed}:{timestep}".encode()

    code = hmac.new(seed.encode(), msg, hashlib.sha256).hexdigest()
    return str(int(code[:6], 16)).zfill(6)


# -----------------------------
#  VERIFY 2FA CODE
# -----------------------------
def verify_2fa_code(seed: str, code: str) -> bool:
    expected = generate_2fa_code(seed)
    return expected == code
