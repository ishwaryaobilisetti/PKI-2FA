import base64
import subprocess
import sys
import os

# ---------------------------------------------------------
# Allow importing utils_crypto.py from /app directory
# ---------------------------------------------------------
sys.path.append(os.path.abspath("app"))

from utils_crypto import (
    load_private_key,
    load_public_key,
    sign_message_rsa_pss,
    encrypt_with_public_key
)

# ---------------------------------------------------------
# Key paths
# ---------------------------------------------------------
STUDENT_PRIVATE_KEY = "app/student_private.pem"
INSTRUCTOR_PUBLIC_KEY = "app/instructor_public.pem"


# ---------------------------------------------------------
# Get latest commit hash
# ---------------------------------------------------------
def get_commit_hash() -> str:
    return (
        subprocess.check_output(["git", "rev-parse", "HEAD"])
        .decode()
        .strip()
    )


# ---------------------------------------------------------
# Sign {repo_url}|{commit_hash}
# ---------------------------------------------------------
def sign_commit(message: str) -> str:
    private_key = load_private_key(STUDENT_PRIVATE_KEY)

    # message must be encoded to bytes
    message_bytes = message.encode()

    # returns BASE64 STRING
    signature_b64 = sign_message_rsa_pss(private_key, message_bytes)

    return signature_b64


# ---------------------------------------------------------
# Encrypt seed using instructor public key
# ---------------------------------------------------------
def encrypt_seed(seed: str) -> str:
    public_key = load_public_key(INSTRUCTOR_PUBLIC_KEY)

    # returns BASE64 STRING
    encrypted_b64 = encrypt_with_public_key(public_key, seed)

    return encrypted_b64


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n--- PKI 2FA Commit Proof Generator ---\n")

    # Get repo URL
    repo_url = (
        subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"]
        )
        .decode()
        .strip()
    )

    commit_hash = get_commit_hash()

    print(f"Repo URL: {repo_url}")
    print(f"Commit Hash: {commit_hash}")

    # Create message to sign
    message = f"{repo_url}|{commit_hash}"

    # Sign it
    signature_b64 = sign_commit(message)

    # Ask for decrypted seed
    seed = input("Enter decrypted seed: ").strip()

    encrypted_seed_b64 = encrypt_seed(seed)

    print("\n--- OUTPUT ---")
    print(f"Repo URL: {repo_url}")
    print(f"Commit Hash: {commit_hash}")
    print(f"Encrypted Signature: {signature_b64}")
    print(f"Encrypted Seed: {encrypted_seed_b64}")

    print("\nSubmit these four values in LMS.\n")
