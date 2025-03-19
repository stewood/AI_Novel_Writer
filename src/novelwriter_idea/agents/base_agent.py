"""Base agent class for all novel writer agents."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from novelwriter_idea.config.llm import LLMConfig

class BaseAgent(ABC):
    """Base class for all agents in the novel writer system."""
    
    def __init__(
        self,
        llm_config: LLMConfig,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the base agent.
        
        Args:
            llm_config: Configuration for the LLM client
            logger: Optional logger instance. If not provided, creates a new one.
        """
        self.llm_config = llm_config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    async def process(self, **kwargs) -> Dict[str, Any]:
        """Process the agent's main task.
        
        Args:
            **kwargs: Additional arguments specific to the agent's implementation
            
        Returns:
            Dict containing the results of the agent's processing
        """
        pass
    
    def _get_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Get a completion from the LLM.
        
        Args:
            prompt: The user prompt to send to the LLM
            system_prompt: Optional system prompt to guide the LLM's behavior
            
        Returns:
            The LLM's response
        """
        self.logger.debug(f"Sending prompt to LLM: {prompt}")
        try:
            response = self.llm_config.get_completion(prompt, system_prompt)
            self.logger.debug(f"Received response from LLM: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error getting completion from LLM: {e}", exc_info=True)
            raise 