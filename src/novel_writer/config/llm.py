"""LLM configuration and client setup.

This module provides configuration and client setup for interacting with Language
Models through OpenRouter. It includes classes for API key management with
support for both free and paid tiers, as well as automatic failover between keys.
"""

import os
import logging
from typing import Optional, List, Dict, Tuple
import httpx
from openai import AsyncOpenAI
import aiohttp

# Initialize logger
logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages multiple API keys for OpenRouter with automatic failover logic.
    
    This class handles the management of both free and paid API keys,
    automatically rotating between them when rate limits are reached and
    transitioning from free to paid tiers when necessary.
    
    Attributes:
        free_keys: List of API keys for free tier models
        paid_keys: List of API keys for paid tier models
        current_key_index: Current index in the active keys list
        using_free_keys: Whether currently using free tier keys
        exhausted_keys: Set of keys that have been marked as exhausted
    """
    
    def __init__(self):
        """Initialize the API key manager."""
        self.free_keys = []
        self.paid_keys = []
        self.current_key_index = 0
        self.using_free_keys = True
        self.exhausted_keys = set()
        
    def add_free_key(self, key: str) -> None:
        """Add a free API key to the manager.
        
        Args:
            key: The API key to add
        """
        if key and key not in self.free_keys:
            self.free_keys.append(key)
            logger.debug(f"Added free API key (ending: ...{key[-8:]})")
    
    def add_paid_key(self, key: str) -> None:
        """Add a paid API key to the manager.
        
        Args:
            key: The API key to add
        """
        if key and key not in self.paid_keys:
            self.paid_keys.append(key)
            logger.debug(f"Added paid API key (ending: ...{key[-8:]})")
    
    def get_current_key(self) -> Tuple[str, bool]:
        """Get the current API key to use.
        
        Returns:
            Tuple of (api_key, is_free_tier)
        
        Raises:
            ValueError: If no keys are available
        """
        # First try free keys if we're in free mode
        if self.using_free_keys and self.free_keys:
            keys_list = self.free_keys
            is_free = True
        # Otherwise use paid keys
        elif self.paid_keys:
            keys_list = self.paid_keys
            is_free = False
            if self.using_free_keys:
                logger.info("Switching from free to paid API keys")
                self.using_free_keys = False
                self.current_key_index = 0
        else:
            # No keys available
            raise ValueError("No API keys available")
        
        # Get the current key
        if not keys_list:
            raise ValueError("No API keys available in the current tier")
        
        # If all keys in the current list are exhausted, reset
        all_exhausted = all(key in self.exhausted_keys for key in keys_list)
        if all_exhausted:
            logger.info(f"All {'free' if is_free else 'paid'} keys were exhausted, resetting")
            self.exhausted_keys.clear()
        
        # Get the key
        key = keys_list[self.current_key_index % len(keys_list)]
        return key, is_free
    
    def mark_key_exhausted(self, key: str) -> None:
        """Mark a key as exhausted and rotate to the next available key.
        
        Args:
            key: The key to mark as exhausted
        """
        logger.info(f"Marking API key as exhausted (ending: ...{key[-8:]})")
        self.exhausted_keys.add(key)
        self.rotate_key()
    
    def rotate_key(self) -> None:
        """Rotate to the next available key."""
        if self.using_free_keys and self.free_keys:
            self.current_key_index = (self.current_key_index + 1) % len(self.free_keys)
            logger.debug(f"Rotated to next free key index: {self.current_key_index}")
            
            # If we've rotated through all free keys, switch to paid
            all_free_exhausted = all(key in self.exhausted_keys for key in self.free_keys)
            if all_free_exhausted:
                logger.info("All free keys exhausted, switching to paid keys")
                self.using_free_keys = False
                self.current_key_index = 0
        else:
            # Using paid keys
            if self.paid_keys:
                self.current_key_index = (self.current_key_index + 1) % len(self.paid_keys)
                logger.debug(f"Rotated to next paid key index: {self.current_key_index}")

    def get_api_key(self, use_free: bool = True) -> str:
        """Get the next available API key.
        
        Args:
            use_free: Whether to use a free API key. If True, returns a free key if available,
                     otherwise returns a paid key. If False, returns a paid key if available.
        
        Returns:
            str: The API key to use
            
        Raises:
            ValueError: If no API keys are available
        """
        if use_free and self.free_keys:
            key = self.free_keys[self.current_key_index]
            self.current_key_index = (self.current_key_index + 1) % len(self.free_keys)
            return key
            
        if self.paid_keys:
            key = self.paid_keys[self.current_key_index]
            self.current_key_index = (self.current_key_index + 1) % len(self.paid_keys)
            return key
            
        raise ValueError("No API keys available")

class LLMConfig:
    """Configuration for LLM integration.
    
    This class manages configuration for Language Model integration including 
    API keys, model selection, and parameter settings. It supports both
    direct key usage and managed keys via APIKeyManager.
    
    Attributes:
        api_key_manager: Optional API key manager for multiple keys
        single_api_key: Single API key (used when manager not provided)
        base_url: API endpoint URL
        free_model: Model ID for free tier
        paid_model: Model ID for paid tier
        temperature: Sampling temperature for generation (0.0-1.0)
        max_tokens: Maximum tokens to generate per request
        _is_using_free_model: Whether currently using free tier model
    """
    
    def __init__(self, api_key_manager: APIKeyManager = None, api_key: str = None, base_url: str = None):
        """Initialize the LLM configuration.
        
        Args:
            api_key_manager: API key manager to use for multiple keys
            api_key: Single API key to use (if manager not provided)
            base_url: Optional base URL for the API
            
        Raises:
            ValueError: If neither api_key_manager nor api_key is provided
        """
        if not api_key_manager and not api_key:
            raise ValueError("Either api_key_manager or api_key is required")
        
        self.api_key_manager = api_key_manager
        self.single_api_key = api_key
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self.free_model = "google/gemma-3-27b-it:free"
        self.paid_model = "google/gemma-3-27b-it"
        self.temperature = 0.7
        self.max_tokens = 2000
        self._is_using_free_model = False
    
    @property
    def model(self) -> str:
        """Get the current model to use.
        
        Returns:
            The model identifier (free or paid tier)
        """
        return self.free_model if self._is_using_free_model else self.paid_model
    
    def _get_current_key(self) -> str:
        """Get the current API key to use.
        
        Returns:
            The API key
            
        Raises:
            ValueError: If no keys are available
        """
        if self.api_key_manager:
            key, is_free = self.api_key_manager.get_current_key()
            self._is_using_free_model = is_free
            return key
        return self.single_api_key

    def get_client(self) -> AsyncOpenAI:
        """Get an authenticated OpenAI client.
        
        Returns:
            Configured AsyncOpenAI client
        """
        api_key = self._get_current_key()
        
        # Initialize the client with the API key directly
        client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=api_key,  # Use the API key directly
            http_client=httpx.AsyncClient(
                timeout=60.0,
                headers={
                    "HTTP-Referer": "https://github.com/stewood/AI_Novel_Writer",
                    "X-Title": "AI Novel Writer - Stephen Woodard",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
        )
        
        return client

    async def get_completion(self, prompt: str) -> str:
        """Get a completion from the LLM.
        
        This method sends a prompt to the LLM and returns the generated response.
        It handles API key management, model selection, and error handling.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The generated text response
            
        Raises:
            Exception: If there is an error getting the response
        """
        client = self.get_client()
        
        try:
            # Remove parameters that are set in the class to avoid duplicates
            kwargs = {
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "model": self.model
            }
            kwargs.pop('max_tokens', None)
            kwargs.pop('temperature', None)
            kwargs.pop('model', None)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "system",
                    "content": "You are a helpful AI assistant."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in get_completion: {str(e)}")
            raise

    async def generate_text(self, prompt: str) -> str:
        """Generate text using the LLM.
        
        This method is an alias for get_completion, providing a more intuitive
        name for text generation tasks.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The generated text response
            
        Raises:
            Exception: If there is an error generating the text
        """
        return await self.get_completion(prompt)

    def set_temperature(self, temperature: float) -> None:
        """Set the sampling temperature for generation.
        
        Args:
            temperature: Value between 0.0 and 1.0
                - 0.0: More deterministic, focused outputs
                - 1.0: More creative, diverse outputs
                
        Raises:
            ValueError: If temperature is not between 0.0 and 1.0
        """
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        self.temperature = temperature
        
    def set_max_tokens(self, max_tokens: int) -> None:
        """Set the maximum number of tokens to generate.
        
        Args:
            max_tokens: Maximum number of tokens (1-4000)
                
        Raises:
            ValueError: If max_tokens is not between 1 and 4000
        """
        if not 1 <= max_tokens <= 4000:
            raise ValueError("Max tokens must be between 1 and 4000")
        self.max_tokens = max_tokens

    def _get_api_key(self) -> str:
        """Get an API key to use.
        
        Returns:
            API key string
        """
        if self.single_api_key:
            return self.single_api_key
            
        if self.api_key_manager:
            return self.api_key_manager.get_api_key(self._is_using_free_model)
            
        raise Exception("No API key available") 