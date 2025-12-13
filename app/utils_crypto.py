import base64
import time
import hmac
import hashlib
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


# -----------------------------
#  RSA KEY GENERATION
# -----------------------------
def generate_rsa_keypair(key_size: int = 2048):
    """
    Generate RSA private & public key pair
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    public_key = private_key.public_key()
    return private_key, public_key


# -----------------------------
#  LOAD KEYS
# -----------------------------
def load_private_key(path: str):
    with open(path, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )


def load_public_key(path: str):
    with open(path, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())


# -----------------------------
#  DECRYPT SEED
# -----------------------------
def decrypt_seed(encrypted_seed_b64: str) -> str:
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
#  RSA SIGN
# -----------------------------
def sign_message_rsa_pss(private_key, message_bytes: bytes) -> str:
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
#  RSA ENCRYPT
# -----------------------------
def encrypt_with_public_key(public_key, message: str) -> str:
    if isinstance(message, str):
        message = message.encode()

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
#  VERIFY 2FA
# -----------------------------
def verify_2fa_code(seed: str, code: str) -> bool:
    expected = generate_2fa_code(seed)
    return expected == code
