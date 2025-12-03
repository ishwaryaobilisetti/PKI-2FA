from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path

from app.utils_crypto import (
    load_private_key,
    decrypt_seed,
    generate_totp_code,
    verify_totp_code
)

DATA_DIR = Path("/data")
SEED_FILE = DATA_DIR / "seed.txt"
PRIVATE_KEY_PATH = Path("student_private.pem")

app = FastAPI(title="PKI TOTP Microservice")


class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(req: DecryptRequest):
    try:
        private_key = load_private_key(PRIVATE_KEY_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load private key: {e}")

    try:
        hex_seed = decrypt_seed(req.encrypted_seed, private_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {e}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(SEED_FILE, "w") as f:
        f.write(hex_seed)

    return {"status": "ok", "seed_saved": True}


@app.get("/generate-2fa")
async def generate_2fa():
    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_FILE.read_text().strip()

    try:
        code = generate_totp_code(hex_seed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TOTP generation failed: {e}")

    import time
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}


@app.post("/verify-2fa")
async def verify_2fa(req: VerifyRequest):
    code = req.code

    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_FILE.read_text().strip()

    try:
        valid = verify_totp_code(hex_seed, code, valid_window=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {e}")

    return {"valid": bool(valid)}