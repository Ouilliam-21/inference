from models.models import Model
from transformers import AutoModelForCausalLM, AutoTokenizer


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
    
    def generate(self, user_input: str) -> str:
        """Generate a response from the LLM"""
        if not self.is_loaded:
            raise RuntimeError("Model must be loaded before generating. Call load() first.")
        
        messages = [
            {"role": "system", "content": "You're name is John Doe and you're a helpful french assistant, you always answer in json format like this: {\"answer\": \"your answer here\"}"},
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

        thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

        print("thinking content:", thinking_content)
        print("content:", content)

        return content