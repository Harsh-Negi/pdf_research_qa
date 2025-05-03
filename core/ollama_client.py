"""
Ollama API Client for PDF Research Q&A
Handles communication with the Ollama API for text generation and embeddings.
"""

import requests
from typing import List, Dict, Any, Optional

class OllamaClient:
    def __init__(self, model: str, embedding_model: str = "nomic-embed-text:latest", host: str = "localhost", port: int = 11434):
        """Initialize the Ollama client with the specified model."""
        self.model = model
        self.embedding_model = embedding_model
        self.base_url = f"http://{host}:{port}/api"

    def generate(self, prompt: str, system_prompt: str = None, context: str = None) -> str:
        """Generate a response from the model."""
        url = f"{self.base_url}/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        if context:
            payload["context"] = context
            
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code}\n{response.text}"

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get an embedding for the given text."""
        url = f"{self.base_url}/embeddings"
        
        payload = {
            "model": self.embedding_model,
            "prompt": text
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    def list_models(self) -> List[str]:
        """Get a list of available models."""
        url = f"{self.base_url}/tags"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                models = [model["name"] for model in response.json()["models"]]
                return models
            else:
                print(f"Error listing models: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            return []