from fastapi import FastAPI, UploadFile, File, Form
from claims_agent import ClaimsAgent
from portfolio_api import router as portfolio_router
from typing import Dict

app = FastAPI()
app.include_router(portfolio_router)
agent = ClaimsAgent()

@app.post("/process-claim/")
def process_claim(file: UploadFile = File(...), policy_doc: str = Form(...)) -> Dict:
    """
    Endpoint to process an insurance claim document.
    """
    result = agent.process_claim(file, policy_doc)
    return result

@app.get("/")
def root():
    return {"message": "Intelligent Claims Processing System API"}
