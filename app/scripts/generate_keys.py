import sys
from pathlib import Path

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.utils_crypto import generate_rsa_keypair

if __name__ == "__main__":
    generate_rsa_keypair(
        private_path=str(ROOT / "student_private.pem"),
        public_path=str(ROOT / "student_public.pem")
    )
    print("Keys generated successfully at project root!")
