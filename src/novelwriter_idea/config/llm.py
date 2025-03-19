"""LLM configuration and client setup."""

import os
from typing import Optional
import httpx
from openai import AsyncOpenAI

class LLMConfig:
    """Configuration for LLM integration."""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "google/gemma-3-27b-it:free"
        self.temperature = 0.7
        self.max_tokens = 2000

    def get_client(self) -> AsyncOpenAI:
        default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/stewood/AI_Novel_Writer",
            "X-Title": "AI Novel Writer - Stephen Woodard",
            "X-Email": "stewood@outlook.com"
        }
        
        return AsyncOpenAI(
            base_url=self.base_url,
            api_key="not-needed",  # API key is sent in headers
            default_headers=default_headers,
            http_client=httpx.AsyncClient()
        )

    async def get_completion(self, prompt: str, temperature: float = None) -> str:
        client = self.get_client()
        messages = []
        messages.append({"role": "user", "content": prompt})

        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens
            )
            content = response.choices[0].message.content
            print(f"Raw LLM response: {content}")  # Debug logging
            return content
        except Exception as e:
            error_msg = f"Error making request: {str(e)}"
            print(error_msg)
            raise e 