# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from service import evaluate_tourist

app = FastAPI(title="Tourist Monitor AI")

class TouristData(BaseModel):
    tourist_id: str
    latitude: float
    longitude: float
    timestamp: str
    dwell_time: float = 0
    age: int = 30
    disabilities: bool = False
    health_conditions: bool = False

@app.post("/evaluate")
async def evaluate(data: TouristData):
    """
    Evaluate a tourist's safety based on location, speed, dwell time, and anomalies.
    """
    result = evaluate_tourist(data.dict())
    return result

@app.get("/")
def health_check():
    return {"status": "Tourist Monitor AI is running"}
