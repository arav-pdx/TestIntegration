from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
import requests

app = FastAPI()


fake_db = {}

@app.get("/")
def read_root():
    return {"message": "FastAPI to ASP.NET Core bridge working"}

@app.get("/square/{number}")
def get_square(number: int):
    try:
        response = requests.get(f"http://localhost:8000/example/square/{number}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}


