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
    
    @abstractmethod
    def unload(self) -> None:
        """Unload the model from memory"""
        pass
    
    @abstractmethod
    def generate(self, *args, **kwargs) -> str:
        """Generate output (text for LLM, audio for TTS)"""
        pass