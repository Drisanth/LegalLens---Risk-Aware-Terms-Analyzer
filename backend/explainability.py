import torch
from .models import model_loader
from .config import Config

class ExplainabilityEngine:
    def __init__(self):
        pass

    def explain_clause(self, clause_text):
        """
        Returns token importance scores based on attention weights.
        """
        tokenizer, model = model_loader.get_embedding_model()
        
        inputs = tokenizer(clause_text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(Config.DEVICE) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)
        
        # Aggregating attention
        # Shape: (batch, num_heads, seq_len, seq_len)
        # We process one clause at a time here
        attentions = outputs.attentions[-1] # Last layer
        # Average across heads: (1, seq_len, seq_len)
        avg_attention = torch.mean(attentions, dim=1).squeeze(0)
        
        # Look at attention of [CLS] token (idx 0) to other tokens
        cls_attention = avg_attention[0, :]
        
        tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        scores = cls_attention.cpu().numpy()
        
        # Filter special tokens
        explanation = []
        for token, score in zip(tokens, scores):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                # Clean subwords (##)
                readable_token = token.replace("##", "")
                explanation.append({
                    "token": readable_token,
                    "score": float(score)
                })
                
        # Sort by score descending
        explanation.sort(key=lambda x: x['score'], reverse=True)
        
        return explanation[:10] # Top 10 words

explainability_engine = ExplainabilityEngine()
