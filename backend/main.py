from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import shutil
import os
import pdfminer.high_level

from .risk_engine import risk_engine
from .summarizer import summarizer_engine
from .explainability import explainability_engine
from .config import Config

app = FastAPI(title="LegalLens API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserProfile(BaseModel):
    sensitivity: float = 0.5
    weights: Dict[str, float] = {}

class AnalysisResponse(BaseModel):
    overall_risk_score: float
    clause_level_scores: List[Dict[str, Any]]
    propagated_scores: List[float] # Just for debugging/graph
    risk_categories: Dict[str, List[str]]
    summary: str
    explanations: Dict[int, List[Dict[str, float]]]
    graph_metadata: Dict[str, Any]

class PersonalizeRequest(BaseModel):
    clauses: List[Dict[str, Any]]
    user_profile: UserProfile

@app.get("/")
def health_check():
    return {"status": "ok", "device": str(Config.DEVICE)}

@app.post("/analyze")
async def analyze_document(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    sensitivity: float = Form(0.5)
):
    content = ""
    if text:
        content = text
    elif file:
        # Extract text from file
        filename = file.filename
        if filename.endswith(".pdf"):
            temp_file = "temp.pdf"
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            content = pdfminer.high_level.extract_text(temp_file)
            os.remove(temp_file)
        elif filename.endswith(".txt"):
            content = (await file.read()).decode("utf-8")
        else:
             raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt or .pdf")
    else:
        raise HTTPException(status_code=400, detail="No text or file provided")

    if not content.strip():
        raise HTTPException(status_code=400, detail="Empty document")

    # 1. Process Risk
    # Initial profile with just sensitivity from form
    user_profile = {"sensitivity": sensitivity, "weights": {}}
    clauses, graph_data = risk_engine.process_document(content, user_profile)
    
    # 2. Summarize
    summary = summarizer_engine.generate_summary(clauses)
    
    # 3. Explain High Risks
    explanations = {}
    overall_risk_sum = 0.0
    
    risk_categories_found = {}
    propagated_list = []
    
    for c in clauses:
        # Aggregate categories
        for cat in c['categories']:
            if cat not in risk_categories_found:
                risk_categories_found[cat] = []
            risk_categories_found[cat].append(c['id'])
            
        propagated_list.append(c['propagated_risk'])
        overall_risk_sum += c['final_risk']
        
        # Explain if risk > 0.6
        if c['final_risk'] > 0.6:
            exp_tokens = explainability_engine.explain_clause(c['text'])
            explanations[c['id']] = exp_tokens
            
    avg_risk = overall_risk_sum / len(clauses) if clauses else 0.0
    
    return {
        "overall_risk_score": avg_risk,
        "clause_level_scores": clauses,
        "propagated_scores": propagated_list,
        "risk_categories": risk_categories_found,
        "summary": summary,
        "explanations": explanations,
        "graph_metadata": graph_data
    }

@app.post("/personalize")
async def personalize_risk(data: PersonalizeRequest):
    # Recalculate risk scores based on new profile without re-embedding
    # This is a simplified logic duplicating the formula in risk_engine
    # Ideally risk_engine should have a 'reweight' method
    
    updated_clauses = []
    
    for c in data.clauses:
        base = c['base_risk']
        p_risk = c['propagated_risk'] # Trust the client passed this back or re-calculate if we had graph
        
        # We need categories. Assumed 'c' has 'categories'
        cats = c.get('categories', [])
        
        beta = Config.DEFAULT_BETA
        sensitivity = data.user_profile.sensitivity
        
        cat_boost = 0.0
        for cat in cats:
            cat_boost += data.user_profile.weights.get(cat, 0.0)
            
        # Re-apply formula
        adjusted = p_risk * (1 + (beta * cat_boost) + (0.1 * sensitivity))
        final = min(adjusted, 1.0)
        
        c['final_risk'] = final
        updated_clauses.append(c)
        
    return {"clause_level_scores": updated_clauses}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
