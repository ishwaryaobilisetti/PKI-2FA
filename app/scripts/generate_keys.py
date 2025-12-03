from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2] / "app"))
from app.utils_crypto import generate_rsa_keypair
if __name__ == "__main__":
 generate_rsa_keypair(private_path="../student_private.pem", public_path="../student_public.pem")
 print("Generated ../student_private.pem and ../student_public.pem")