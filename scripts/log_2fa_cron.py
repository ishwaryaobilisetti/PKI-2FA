#!/usr/bin/env python3
import os
import datetime
import base64
import pyotp
from pathlib import Path

# Docker absolute paths
SEED_FILE = Path("/data/seed.txt")
LOG_FILE = Path("/cron/last_code.txt")

def log_2fa():
    # 1. Read Seed
    if not SEED_FILE.exists():
        # Don't print error every minute, just wait for the API to save the seed
        return

    try:
        hex_seed = SEED_FILE.read_text().strip()
        
        # 2. Generate TOTP Logic (Internalized)
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        
        # Use standard TOTP settings (interval=30s, 6 digits)
        totp = pyotp.TOTP(base32_seed)
        code = totp.now()
        
        # 3. Log with Timestamp
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{now} - 2FA Code: {code}\n"
        
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
            
        print(f"{log_entry.strip()}")

    except Exception as e:
        print(f"Error in Cron script: {e}")

if __name__ == "__main__":
    log_2fa()