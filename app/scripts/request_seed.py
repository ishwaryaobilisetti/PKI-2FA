import sys
from pathlib import Path
import json
import requests
import base64

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

STUDENT_ID = "23A91A61A6"
GITHUB_REPO_URL = "https://github.com/ishwaryaobilisetti/PKI-2FA"
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def main():
    pubkey_path = ROOT / "student_public.pem"
    if not pubkey_path.exists():
        raise FileNotFoundError(f"student_public.pem not found at {pubkey_path}")

    pubkey = pubkey_path.read_text()

    payload = {
        "student_id": STUDENT_ID,
        "github_repo_url": GITHUB_REPO_URL,
        "public_key": pubkey
    }

    print("Sending request to instructor API...")
    response = requests.post(API_URL, json=payload)

    print("Status code:", response.status_code)
    data = response.json()
    print("Response:", data)

    if "encrypted_seed" not in data:
        raise ValueError("API did not return encrypted_seed")

    seed_b64 = data["encrypted_seed"]

    # Save encrypted_seed.txt in project root
    out_path = ROOT / "encrypted_seed.txt"
    out_path.write_text(seed_b64)

    print(f"\nEncrypted seed saved to: {out_path}")
    print("DO NOT commit this file to Git!")

if __name__ == "__main__":
    main()
