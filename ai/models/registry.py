from ai.models.llm.DolphinGGUF import DolphinGGUF
from ai.models.llm.Qwen import Qwen
from ai.models.models import Model
from ai.models.tts.Facebook import FacebookMms

class ModelRegistry:
    """Singleton registry for managing models"""
    
    def __init__(self):
        self._llm_models = {
            "Qwen/Qwen3-0.6B": Qwen(),
            "dphn/Dolphin-X1-8B-GGUF": DolphinGGUF(),
            "dphn/Dolphin3.0-Llama3.1-8B-GGUF-F16": DolphinGGUF(
                "dphn/Dolphin3.0-Llama3.1-8B-GGUF", 
                "Dolphin3.0-Llama3.1-8B-F16.gguf"
            ),
            "dphn/Dolphin3.0-Llama3.1-8B-GGUF-Q8": DolphinGGUF(
                "dphn/Dolphin3.0-Llama3.1-8B-GGUF", 
                "Dolphin3.0-Llama3.1-8B-Q8_0.gguf"
            ),
            "NEO matrix 20b Q8": DolphinGGUF(
                "DavidAU/OpenAi-GPT-oss-20b-abliterated-uncensored-NEO-Imatrix-gguf", 
                "OpenAI-20B-NEOPlus-Uncensored-Q8_0.gguf"
            ),
            "HERETIC 20b Q8": DolphinGGUF(
                "DavidAU/OpenAi-GPT-oss-20b-HERETIC-uncensored-NEO-Imatrix-gguf", 
                "OpenAI-20B-NEOPlus-Uncensored-Q8_0.gguf"
            ),
        }

        self._tts_models = {
            "facebook/mms-tts-fra": FacebookMms(),
            "facebook/mms-tts-eng": FacebookMms("facebook/mms-tts-eng")
        }

        self._current_llm = self._llm_models['Qwen/Qwen3-0.6B']
        self._current_tts = self._tts_models['facebook/mms-tts-fra']
        
        self._current_llm.load()
        self._current_tts.load()

    @property
    def llm_models(self) -> dict[str, Model]:
        return self._llm_models
    
    @property
    def tts_models(self) -> dict[str, Model]:
        return self._tts_models
    
    @property
    def current_llm(self) -> Model:
        return self._current_llm
    
    @current_llm.setter
    def current_llm(self, model: Model):
        self._current_llm = model
    
    @property
    def current_tts(self) -> Model:
        return self._current_tts
    
    @current_tts.setter
    def current_tts(self, model: Model):
        self._current_tts = model
