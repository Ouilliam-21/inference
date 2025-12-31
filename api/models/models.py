from abc import ABC, abstractmethod
import torch


class Model(ABC):
    """Abstract base class for all models (LLM and TTS)"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
    
    
    @abstractmethod
    def load(self) -> None:
        """Load the model into memory"""
        pass
    
    def unload(self) -> None:
        """Unload the model from memory"""
        if self.is_loaded:
            print(f"🔄 Unloading model: {self.model_name}")
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self.is_loaded = False
            print(f"✅ Model unloaded: {self.model_name}")
    
    @abstractmethod
    def generate(self, *args, **kwargs) -> str:
        """Generate output (text for LLM, audio for TTS)"""
        pass