from fastapi import APIRouter, UploadFile, File, Form
from typing import Dict
import requests
import json

router = APIRouter()

GROK_API_KEY = "sk-CWfGRX7vvdGpMHdFoykIYw"
GROK_API_URL = "http://localhost:11434/v1/chat/completions" # Official GenAI Lab endpoint

@router.post("/upload-portfolio/")
async def upload_portfolio(file: UploadFile = File(...)) -> Dict:
    content = await file.read()
    try:
        if file.filename.endswith('.json'):
            portfolio_data = json.loads(content.decode())
        else:
            import pandas as pd
            from io import StringIO
            df = pd.read_csv(StringIO(content.decode()))
            portfolio_data = df.to_dict(orient='records')
    except Exception as e:
        return {"status": "error", "message": str(e)}
    return {"status": "success", "portfolio_data": portfolio_data}

@router.post("/generate-summary/")
def generate_summary(portfolio_data: str = Form(...), client_profile: str = Form(...)) -> Dict:
    """
    Generate portfolio summary using Grok API.
    """
    prompt = (
        f"Generate a personalized investment portfolio summary for the following data:\n"
        f"Portfolio Data: {portfolio_data}\n"
        f"Client Profile: {client_profile}\n"
        f"Include performance, asset allocation, and actionable insights."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 512
    }
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        result = response.json()
        # OpenAI-compatible: extract from 'choices'
        if "choices" in result and len(result["choices"]) > 0:
            summary = result["choices"][0]["message"]["content"]
        else:
            summary = result.get("summary", response.text)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}

@router.post("/export-summary/")
def export_summary(summary: str = Form(...), format: str = Form(...)) -> Dict:
    # Placeholder: implement export logic (PDF, DOCX, HTML)
    return {"status": "success", "message": f"Summary exported as {format}."}