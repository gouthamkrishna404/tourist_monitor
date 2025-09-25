# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from service import evaluate_tourist

app = FastAPI(title="Tourist Safety Monitor API")

class TouristData(BaseModel):
    tourist_id: str
    latitude: float
    longitude: float
    timestamp: str  # ISO format string
    dwell_time: float = 0
    age: int = 30
    disabilities: bool = False
    health_conditions: bool = False

@app.post("/evaluate")
async def evaluate(data: TouristData):
    """
    Endpoint to evaluate a tourist's safety score and risk based on their location data.
    Returns risk level, alerts, and safety score.
    """
    result = evaluate_tourist(data.dict())
    return result

@app.get("/")
async def root():
    return {"message": "Tourist Monitor AI is running!"}
