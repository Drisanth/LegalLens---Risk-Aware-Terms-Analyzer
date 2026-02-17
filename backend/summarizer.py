from .models import model_loader
from .config import Config
import torch

class Summarizer:
    def __init__(self):
        pass

    def generate_summary(self, risk_analysis_results):
        """
        Generates a summary that prioritizes high-risk clauses.
        risk_analysis_results: List of dicts from RiskEngine.
        """
        tokenizer, model = model_loader.get_summarizer_model()
        
        # 1. Extract High Risk Clauses (> 0.7)
        high_risk_clauses = [
            c['text'] for c in risk_analysis_results 
            if c.get('final_risk', 0) > 0.6
        ]
        
        # 2. Extract Low/Medium Risk Clauses
        other_clauses = [
            c['text'] for c in risk_analysis_results 
            if c.get('final_risk', 0) <= 0.6
        ]
        
        summary_sections = []
        
        def summarize_text(text, max_len=150, min_len=40):
            try:
                inputs = tokenizer(
                    [text], 
                    max_length=1024, 
                    truncation=True, 
                    return_tensors="pt"
                )
                inputs = {k: v.to(Config.DEVICE) for k, v in inputs.items()}
                
                with torch.no_grad():
                    summary_ids = model.generate(
                        inputs["input_ids"], 
                        num_beams=4, 
                        max_length=max_len, 
                        min_length=min_len, 
                        early_stopping=True
                    )
                return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            except Exception as e:
                print(f"Summarization error: {e}")
                return text[:200] + "..."

        # Part A: High Risk Warnings (Preserved)
        if high_risk_clauses:
            summary_sections.append("CRITICAL RISK ALERTS:")
            for clause in high_risk_clauses[:5]: # Top 5
                # Summarize if very long
                if len(clause.split()) > 50:
                    short = summarize_text(clause, max_len=60, min_len=10)
                    summary_sections.append(f"- {short}")
                else:
                    summary_sections.append(f"- {clause}")
        
        # Part B: General Summary
        if other_clauses:
            full_text = " ".join(other_clauses)[:2000] # Cap text
            gen_summary = summarize_text(full_text, max_len=150, min_len=50)
            summary_sections.append("\nGENERAL OVERVIEW:")
            summary_sections.append(gen_summary)
            
        return "\n".join(summary_sections)

summarizer_engine = Summarizer()
