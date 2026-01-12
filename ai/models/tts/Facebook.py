from typing import Tuple
from ai.models.models import Model
from transformers import AutoTokenizer, VitsModel
import torch
import scipy
import numpy as np
import uuid

class FacebookMms(Model):
    """Language Model class for text generation"""
    
    def __init__(self, model_name: str = "facebook/mms-tts-fra"):
        super().__init__(model_name)
    
    
    def load(self) -> None:
        """Load the model and tokenizer into memory"""
        if not self.is_loaded:
            print(f"🔄 Loading model: {self.model_name}")
            # Load model directly
            self.model = VitsModel.from_pretrained(self.model_name).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            self.is_loaded = True
            print(f"✅ Model loaded successfully: {self.model_name}")
    
    def generate(self, user_input: str) -> Tuple[str, float]:
        """Generate speech audio from text"""
        if not self.is_loaded:
            raise RuntimeError("Model must be loaded before generating. Call load() first.")
        
        inputs = self.tokenizer(user_input, return_tensors="pt")
        # Move inputs to the same device as the model
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            output = self.model(**inputs).waveform
        
        # Convert torch tensor to numpy array
        audio_numpy = output.cpu().numpy()
        
        # Remove batch dimension if present (shape should be [samples] or [channels, samples])
        if len(audio_numpy.shape) > 1:
            # If shape is [1, samples] or [batch, samples], squeeze
            audio_numpy = audio_numpy.squeeze()
            # If still 2D and shape is [channels, samples], take first channel
            if len(audio_numpy.shape) > 1:
                audio_numpy = audio_numpy[0] if audio_numpy.shape[0] < audio_numpy.shape[1] else audio_numpy[:, 0]
        
        # Ensure audio is 1D
        audio_numpy = audio_numpy.flatten()
        
        # Get sampling rate (ensure it's an integer)
        sampling_rate = int(self.model.config.sampling_rate)
        
        # Normalize audio to [-1, 1] range if needed
        if audio_numpy.dtype in [np.float32, np.float64]:
            # Clip to valid range
            audio_numpy = np.clip(audio_numpy, -1.0, 1.0)
            # Convert to int16 for WAV file
            audio_numpy = (audio_numpy * 32767).astype(np.int16)
        elif audio_numpy.dtype != np.int16:
            # Convert to int16 if not already
            audio_numpy = audio_numpy.astype(np.int16)

        
        output_path = f"tts_output_{uuid.uuid4()}.wav"
        audio_duration = len(audio_numpy) / sampling_rate
        scipy.io.wavfile.write(
            output_path, 
            rate=sampling_rate, 
            data=audio_numpy
        )
        
        return output_path, audio_duration