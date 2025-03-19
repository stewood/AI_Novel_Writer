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
        temperature: Sampling temperature for generation
        max_tokens: Maximum tokens to generate per request
        _is_using_free_model: Whether currently using free tier model
    """
    
    def __init__(self, api_key_manager: APIKeyManager = None, api_key: str = None):
        """Initialize the LLM configuration.
        
        Args:
            api_key_manager: API key manager to use
            api_key: Single API key to use (if manager not provided)
            
        Raises:
            ValueError: If neither api_key_manager nor api_key is provided
        """
        if not api_key_manager and not api_key:
            raise ValueError("Either api_key_manager or api_key is required")
        
        self.api_key_manager = api_key_manager
        self.single_api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.free_model = "google/gemma-3-27b-it:free"
        self.paid_model = "google/gemma-3-27b-it"
        self.temperature = 0.7
        self.max_tokens = 2000
        self._is_using_free_model = True
    
    @property
    def model(self) -> str:
        """Get the current model to use.
        
        Returns:
            The model identifier
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
        
        default_headers = {
            "Authorization": f"Bearer {api_key}",
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
        """Get a completion from the LLM.
        
        Args:
            prompt: The prompt to send
            temperature: Optional temperature override
            
        Returns:
            The completion text
            
        Raises:
            Exception: If there is an error getting the completion
        """
        max_retries = 3
        attempts = 0
        last_exception = None
        
        while attempts < max_retries:
            try:
                client = self.get_client()
                api_key = self._get_current_key()
                current_model = self.model
                
                logger.debug(f"Requesting completion with model: {current_model}")
                logger.superdebug(f"Using API key ending with: ...{api_key[-8:]}")
                
                messages = []
                messages.append({"role": "user", "content": prompt})

                response = await client.chat.completions.create(
                    model=current_model,
                    messages=messages,
                    temperature=temperature or self.temperature,
                    max_tokens=self.max_tokens
                )
                content = response.choices[0].message.content
                return content
                
            except Exception as e:
                last_exception = e
                error_msg = f"Error making request: {str(e)}"
                logger.error(error_msg)
                
                # Check if this is a rate limit or quota error
                error_str = str(e).lower()
                if "rate limit" in error_str or "quota" in error_str or "capacity" in error_str:
                    if self.api_key_manager:
                        logger.warning(f"API key exhausted, rotating to next key")
                        self.api_key_manager.mark_key_exhausted(api_key)
                    else:
                        # Can't rotate with a single key
                        logger.error("Single API key exhausted with no fallback")
                        break
                else:
                    # Other error, don't retry
                    break
                    
                attempts += 1
                
        # If we got here, all retries failed
        logger.error(f"All attempts failed after {attempts} retries")
        raise last_exception 