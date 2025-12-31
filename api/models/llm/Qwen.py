from models.models import Model
from transformers import AutoModelForCausalLM, AutoTokenizer
import json


class Qwen(Model):
    """Language Model class for text generation"""
    
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):
        super().__init__(model_name)
    
    
    def load(self) -> None:
        """Load the model and tokenizer into memory"""
        if not self.is_loaded:
            print(f"🔄 Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
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

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        # conduct text completion
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=32768
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

        # parsing thinking content
        try:
            # rindex finding 151668 (</think>)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

        if content.startswith('{{') and content.endswith('}}'):
            content = content[1:-1]

        return json.loads(content)