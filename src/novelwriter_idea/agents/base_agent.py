"""Base agent class for all agents."""

import logging
from typing import Any, Dict

from novelwriter_idea.config.llm import LLMConfig

class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, llm_config: LLMConfig):
        """Initialize the base agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        self.llm_config = llm_config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Initializing {self.__class__.__name__}")

    async def _get_llm_response(self, prompt: str) -> str:
        """Get a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response as a string
        """
        self.logger.debug(f"Sending prompt to LLM: {prompt}")
        
        try:
            response = await self.llm_config.get_completion(prompt)
            self.logger.superdebug(f"Raw LLM response: {response}")
            
            # Clean up the response
            cleaned = response.strip()
            if cleaned.startswith("```") and cleaned.endswith("```"):
                cleaned = cleaned[3:-3].strip()
            if cleaned.startswith("markdown"):
                cleaned = cleaned[8:].strip()
                
            self.logger.debug(f"Cleaned LLM response: {cleaned}")
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Error getting LLM response: {e}")
            raise 