from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM
from .config import Config
import torch

class ModelLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            instance = super(ModelLoader, cls).__new__(cls)
            try:
                instance._initialize()
                cls._instance = instance
            except Exception as e:
                print(f"FAILED TO INITIALIZE MODEL LOADER: {e}")
                raise e
        return cls._instance
    
    def _initialize(self):
        print("Loading models... (Singleton)")
        
        # 1. Embedding Model (DistilBERT)
        print(f"Loading Embedding Model: {Config.EMBEDDING_MODEL_NAME}...")
        self.tokenizer = AutoTokenizer.from_pretrained(Config.EMBEDDING_MODEL_NAME)
        self.embedding_model = AutoModel.from_pretrained(Config.EMBEDDING_MODEL_NAME)
        self.embedding_model.to(Config.DEVICE)
        self.embedding_model.eval() # No gradient tracking
        
        # 2. Summarization Model
        print(f"Loading Summarizer: {Config.SUMMARIZATION_MODEL_NAME}...")
        self.sum_tokenizer = AutoTokenizer.from_pretrained(Config.SUMMARIZATION_MODEL_NAME)
        self.sum_model = AutoModelForSeq2SeqLM.from_pretrained(Config.SUMMARIZATION_MODEL_NAME)
        self.sum_model.to(Config.DEVICE)
        self.sum_model.eval()

        print("Models loaded successfully.")

    def get_embedding_model(self):
        return self.tokenizer, self.embedding_model

    def get_summarizer_model(self):
        return self.sum_tokenizer, self.sum_model

# Global instance for easy access
model_loader = ModelLoader()
