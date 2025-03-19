"""LLM configuration and client setup."""

import os
from typing import Optional
from openai import OpenAI

class LLMConfig:
    """Configuration for LLM integration."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "google/gemma-3-27b-it:free",
        base_url: str = "https://openrouter.ai/api/v1",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """Initialize LLM configuration."""
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
            
    def get_client(self) -> OpenAI:
        """Get an OpenAI client configured for OpenRouter."""
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/stewood/AI_Novel_Writer",
                "X-Title": "AI Novel Writer"
            }
        )
        
    def get_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Get a completion from the LLM."""
        client = self.get_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content 