from huggingface_hub import hf_hub_download
from models.models import Model
from llama_cpp import Llama
import os   
import json

class DolphinGGUF(Model):
    """Language Model class for text generation"""
    
    def __init__(self, model_name: str = "dphn/Dolphin-X1-8B-GGUF", filename: str = "Dolphin-X1-8B-Q8_0.gguf"):
        super().__init__(model_name)
        self.filename = filename

    def _download_and_load_gguf(self):
        if not os.path.exists(f"./cache/{self.filename}"):
            print(f"Downloading {self.filename}...")
            model_path = hf_hub_download(
                repo_id=self.model_name,
                filename=self.filename,
                local_dir="./cache"
            )
        else:
            model_path = f"./cache/{self.filename}"
            print(f"Model {self.filename} already downloaded")
        
        return model_path
    
    
    def load(self) -> None:
        """Load the model and tokenizer into memory"""
        if not self.is_loaded:
            print(f"🔄 Loading model: {self.model_name}")
            model_path = self._download_and_load_gguf()
            self.model = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_threads=8,
                n_gpu_layers=-1,
                n_batch=512,
                use_mlock=True,
                use_mmap=True,
                verbose=False
            )
            self.is_loaded = True
            print(f"✅ Model loaded successfully: {self.model_name}")

    
    def generate(self, system_prompt: str, user_input: str) -> str:
        """Generate a response from the LLM"""
        if not self.is_loaded:
            raise RuntimeError("Model must be loaded before generating. Call load() first.")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        response = self.model.create_chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )

        res = response['choices'][0]['message']['content'].strip('```json').strip('```')

        if res.startswith('{{') and res.endswith('}}'):
            res = res[1:-1]

        return json.loads(res)
