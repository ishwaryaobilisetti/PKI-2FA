from pathlib import Path
import time
from app.utils_crypto import generate_totp_code

SEED_PATH = Path("/data/seed.txt")
OUT = Path("/cron/last_code.txt")


def main():
    try:
        seed = SEED_PATH.read_text().strip()
        code = generate_totp_code(seed)
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        OUT.write_text(f"{ts} - 2FA Code: {code}\n")
    except Exception as e:
        OUT.write_text(f"Error: {e}\n")


if __name__ == "__main__":
    main()
