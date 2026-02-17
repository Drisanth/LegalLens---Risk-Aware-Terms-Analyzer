import torch
import os

class Config:
    # Device Configuration
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    USE_FP16 = torch.cuda.is_available()
    
    # Model Configuration
    # Using a lightweight model for embeddings as requested
    EMBEDDING_MODEL_NAME = "distilbert-base-uncased" 
    # Using a distilbart for summarization for speed/memory tradeoff
    SUMMARIZATION_MODEL_NAME = "sshleifer/distilbart-cnn-12-6" 
    
    # Risk Engine Configuration
    MAX_SEQ_LENGTH = 512
    CHUNK_SIZE = 512 # Strategy handles this
    
    # Risk Propagation
    DEFAULT_ALPHA = 0.3 # propagation factor
    DEFAULT_BETA = 0.5 # personalization factor
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def print_config():
        print(f"LegalLens Config Loaded:")
        print(f"Device: {Config.DEVICE}")
        print(f"FP16: {Config.USE_FP16}")
        print(f"Embedding Model: {Config.EMBEDDING_MODEL_NAME}")
