import os
from abc import ABC, abstractmethod
import google.generativeai as genai
import openai

# Vertex AI imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel as VertexGenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

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

class VertexAIProvider(ModelProvider):
    """Provider for Google's Vertex AI Gemini models using Application Default Credentials."""
    
    def __init__(self, project_id: str, location: str, model_name: str):
        if not VERTEX_AI_AVAILABLE:
            raise ImportError(
                "google-cloud-aiplatform is not installed. "
                "Install it with: uv add google-cloud-aiplatform"
            )
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        # Validate project_id is not a placeholder
        if not project_id or project_id == "your-gcp-project-id":
            raise ValueError(
                f"Invalid project_id: '{project_id}'. "
                "Please set vertex_ai_project in config.yaml or GOOGLE_CLOUD_PROJECT environment variable."
            )
        
        # Initialize Vertex AI with ADC (will use gcloud auth credentials)
        try:
            vertexai.init(project=project_id, location=location)
            self.model = VertexGenerativeModel(model_name)
        except Exception as e:
            error_msg = str(e)
            if "CONSUMER_INVALID" in error_msg or "403" in error_msg or "Permission denied" in error_msg:
                raise ValueError(
                    f"Vertex AI API access denied for project '{project_id}'.\n\n"
                    "This error typically means:\n"
                    "1. Vertex AI API is not enabled - Enable it at:\n"
                    f"   https://console.cloud.google.com/apis/library/aiplatform.googleapis.com?project={project_id}\n"
                    "2. Billing is not enabled - Ensure billing is active for this project\n"
                    "3. Insufficient permissions - Your account needs 'Vertex AI User' role\n"
                    "4. Wrong project ID - Verify the project ID matches your GCP project\n\n"
                    f"To enable Vertex AI API, run:\n"
                    f"  gcloud services enable aiplatform.googleapis.com --project={project_id}\n\n"
                    f"Original error: {error_msg}"
                ) from e
            raise
        
    @property
    def env_var_name(self) -> str:
        return "GOOGLE_CLOUD_PROJECT"  # Not strictly required, but useful for project detection
        
    def generate_content(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

class OpenAIProvider(ModelProvider):
    """Provider for OpenAI models."""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=self.api_key)
        
    @property
    def env_var_name(self) -> str:
        return "OPENAI_API_KEY"
        
    def generate_content(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
