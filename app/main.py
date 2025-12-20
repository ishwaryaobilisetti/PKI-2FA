from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyotp
import base64
from pathlib import Path

app = FastAPI()
SEED_FILE = Path("/data/seed.txt")

DECRYPTED_SEED = None

if SEED_FILE.exists():
    try:
        DECRYPTED_SEED = SEED_FILE.read_text().strip()
        print(f"Startup: Successfully loaded seed from {SEED_FILE}")
    except Exception as e:
        print(f"Startup Error: Could not read seed file: {e}")

class SeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# Helper Function (Logic from utils_crypto moved here)
def get_totp_obj(hex_seed: str):
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    return pyotp.TOTP(base32_seed)


@app.get("/")
def health_check():
    return {"status": "running", "service": "PKI-2FA"}

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: SeedRequest):
    global DECRYPTED_SEED
    try:
        # Assuming hex_seed for this example
        DECRYPTED_SEED = req.encrypted_seed 
        
        # Save to shared volume so Cron script can see it
        SEED_FILE.write_text(DECRYPTED_SEED)
        
        return {"message": "Seed decrypted and saved for Cron"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate-2fa")
def generate_endpoint():
    if not DECRYPTED_SEED:
        raise HTTPException(status_code=400, detail="Seed not decrypted yet")
    totp = get_totp_obj(DECRYPTED_SEED)
    return {"code": totp.now()}

@app.post("/verify-2fa")
def verify_endpoint(req: VerifyRequest):
    if not DECRYPTED_SEED:
        raise HTTPException(status_code=400, detail="Seed not decrypted yet")
    totp = get_totp_obj(DECRYPTED_SEED)
    return {"valid": totp.verify(req.code)}