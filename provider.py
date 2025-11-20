import os
from abc import ABC, abstractmethod
import google.generativeai as genai

class ModelProvider(ABC):
    """Abstract base class for model providers."""
    
    @property
    @abstractmethod
    def env_var_name(self) -> str:
        """The name of the environment variable required for the API key."""
        pass
    
    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        """Generates content based on the prompt."""
        pass

class GeminiProvider(ModelProvider):
    """Provider for Google's Gemini models."""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
    @property
    def env_var_name(self) -> str:
        return "GEMINI_API_KEY"
        
    def generate_content(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text
