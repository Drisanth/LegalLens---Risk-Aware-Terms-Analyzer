import torch
import numpy as np
from .models import model_loader
from .config import Config
from .graph_engine import GraphEngine
import re

class RiskEngine:
    def __init__(self):
        self.graph_engine = GraphEngine()
        # Define some keywords for heuristic risk scoring (Fallback/Baseline)
        self.risk_categories = {
            "Data Sharing": ["share", "third party", "affiliate", "marketing", "sell data"],
            "Arbitration": ["arbitration", "waive", "jury", "class action", "dispute"],
            "Liability": ["limitation", "liability", "as is", "warranty", "indemnify"],
            "termination": ["terminate", "suspend", "without notice", "sole discretion"]
        }

    def segment_clauses(self, text):
        """
        Splits text into clauses. 
        Simple heuristic: Split by newlines or numbered lists.
        """
        # Remove excessive whitespace
        text = text.strip()
        # Split by double newline (paragraphs) or numbered lists pattern
        # This is a simplified regex for the demo
        clauses = re.split(r'\n\s*\n|\n\s*(?=\d+\.)', text)
        
        cleaned_clauses = []
        for c in clauses:
            c = c.strip()
            if len(c) > 20: # Filter out short headers/noise
                cleaned_clauses.append(c)
                
        return cleaned_clauses

    def compute_embeddings(self, clauses):
        tokenizer, model = model_loader.get_embedding_model()
        embeddings = []
        
        # Batch processing
        batch_size = 8
        for i in range(0, len(clauses), batch_size):
            batch = clauses[i : i + batch_size]
            inputs = tokenizer(batch, padding=True, truncation=True, max_length=Config.MAX_SEQ_LENGTH, return_tensors="pt")
            inputs = {k: v.to(Config.DEVICE) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model(**inputs)
                # Use CLS token embedding
                batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                embeddings.extend(batch_embeddings)
                
            if Config.DEVICE.type == "cuda":
                torch.cuda.empty_cache()
                
        return np.array(embeddings)

    def calculate_base_risk(self, clause_text):
        """
        Heuristic base risk calculation.
        In a full version, this would be a trained classifier head.
        """
        text_lower = clause_text.lower()
        score = 0.0
        detected_categories = []
        
        for category, keywords in self.risk_categories.items():
            for kw in keywords:
                if kw in text_lower:
                    score += 0.2
                    detected_categories.append(category)
                    # Cap at 1 per category for simplicity in this heuristic
                    break
        
        return min(score, 1.0), detected_categories

    def process_document(self, text, user_profile=None):
        # 1. Segment
        clauses_text = self.segment_clauses(text)
        
        # 2. Embed
        embeddings = self.compute_embeddings(clauses_text)
        
        # 3. Base Risk Calculation
        clause_data = []
        for idx, txt in enumerate(clauses_text):
            base_score, categories = self.calculate_base_risk(txt)
            clause_data.append({
                "id": idx,
                "text": txt,
                "base_risk": base_score,
                "categories": categories
            })
            
        # 4. Build Graph & Propagate
        self.graph_engine.build_graph(clause_data, embeddings)
        propagated_risks = self.graph_engine.propagate_risk(alpha=Config.DEFAULT_ALPHA)
        
        # 5. Personalization
        # user_profile = {"sensitivity": 0.5, "weights": {"Data Sharing": 1.5, ...}} (Example)
        final_scores = []
        
        for idx, data in enumerate(clause_data):
            p_risk = propagated_risks.get(idx, 0.0)
            
            # Apply Personalization
            if user_profile:
                # Example: R_personalized = R_propagated * (1 + beta * user_weight)
                beta = Config.DEFAULT_BETA
                sensitivity = user_profile.get("sensitivity", 0.5)
                # boost based on categories
                cat_boost = 0.0
                for cat in data['categories']:
                    cat_boost += user_profile.get("weights", {}).get(cat, 0.0)
                
                adjusted_risk = p_risk * (1 + (beta * cat_boost) + (0.1 * sensitivity))
                final_score = min(adjusted_risk, 1.0)
            else:
                final_score = p_risk
            
            final_scores.append({
                "id": idx,
                "text": data['text'],
                "base_risk": data['base_risk'],
                "propagated_risk": p_risk,
                "final_risk": final_score,
                "categories": data['categories']
            })
            
        return final_scores, self.graph_engine.get_graph_metadata()

risk_engine = RiskEngine()
