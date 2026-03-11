from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv() # Carga tu .env

app = FastAPI(title="Sentin3l")

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "system": "Sentin3l",
        "security_level": "High"
    }