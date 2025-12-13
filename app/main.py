from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils_crypto import decrypt_seed, generate_2fa_code, verify_2fa_code

app = FastAPI()

class SeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    seed: str
    code: str

@app.get("/")
def root():
    return {"message": "PKI 2FA student service running"}

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: SeedRequest):
    try:
        seed = decrypt_seed(req.encrypted_seed)
        return {"seed": seed}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/generate-2fa")
def generate_endpoint(seed: str):
    try:
        code = generate_2fa_code(seed)
        return {"code": code}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/verify-2fa")
def verify_endpoint(req: VerifyRequest):
    try:
        return {"valid": verify_2fa_code(req.seed, req.code)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
