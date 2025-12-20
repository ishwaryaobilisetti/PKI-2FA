import sys
import os

# Add project root to PYTHONPATH
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

from cryptography.hazmat.primitives import serialization
from app.utils_crypto import generate_rsa_keypair


def main():
    private_key, public_key = generate_rsa_keypair()

    with open("student_private.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption()
            )
        )

    with open("student_public.pem", "wb") as f:
        f.write(
            public_key.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print("RSA key pair generated successfully")


if __name__ == "__main__":
    main()
