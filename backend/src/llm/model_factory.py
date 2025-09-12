"""
LangChain integration with configurable models (OpenAI, Claude).

This module provides a unified interface for different LLM providers,
allowing the application to switch between models seamlessly.
"""

import logging
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List, Union

# Import LangChain components
try:
    from langchain.llms.base import LLM
    from langchain.chat_models import ChatOpenAI
    from langchain.chat_models import ChatAnthropic
    from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
except ImportError as e:
    logging.warning(f"LangChain import failed: {e}. Using mock implementations.")
    # Define mock classes for development without LangChain

    class LLM:
        pass

    class ChatOpenAI:
        def __init__(self, **kwargs):
            pass

    class ChatAnthropic:
        def __init__(self, **kwargs):
            pass

    class BaseMessage:
        pass

    class HumanMessage:
        def __init__(self, content: str):
            self.content = content

    class SystemMessage:
        def __init__(self, content: str):
            self.content = content

    class AIMessage:
        def __init__(self, content: str):
            self.content = content


logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""

    OPENAI_GPT4 = "gpt-4"
    OPENAI_GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    MOCK = "mock"  # For testing and development


class LLMConfig:
    """Configuration for LLM models."""

    def __init__(
        self,
        provider: LLMProvider,
        temperature: float = 0.7,
        max_tokens: int = 500,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize LLM configuration.

        Args:
            provider: LLM provider enum
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty for repetition
            presence_penalty: Presence penalty for repetition
            api_key: API key for the provider
            **kwargs: Additional provider-specific parameters
        """
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.api_key = api_key
        self.extra_params = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "provider": self.provider.value,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            **self.extra_params,
        }


class BaseLLMModel(ABC):
    """Abstract base class for LLM models."""

    def __init__(self, config: LLMConfig):
        """
        Initialize LLM model.

        Args:
            config: LLM configuration
        """
        self.config = config
        self._model = None

    @abstractmethod
    async def generate_response(self, messages: List[BaseMessage], **kwargs) -> str:
        """
        Generate response from messages.

        Args:
            messages: List of messages for the conversation
            **kwargs: Additional generation parameters

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.

        Returns:
            Dictionary with model information
        """
        pass


class OpenAIModel(BaseLLMModel):
    """OpenAI GPT model implementation."""

    def __init__(self, config: LLMConfig):
        """Initialize OpenAI model."""
        super().__init__(config)

        # Get API key from config or environment
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not provided. Using mock mode.")
            self._mock_mode = True
            return

        self._mock_mode = False
        try:
            self._model = ChatOpenAI(
                model_name=config.provider.value,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                openai_api_key=api_key,
                **config.extra_params,
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI model: {e}")
            self._mock_mode = True

    async def generate_response(self, messages: List[BaseMessage], **kwargs) -> str:
        """Generate response using OpenAI model."""
        if self._mock_mode:
            return await self._mock_response(messages)

        try:
            response = await self._model.agenerate([messages])
            return response.generations[0][0].text.strip()
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return await self._mock_response(messages)

    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information."""
        return {
            "provider": "OpenAI",
            "model": self.config.provider.value,
            "mock_mode": self._mock_mode,
            "config": self.config.to_dict(),
        }

    async def _mock_response(self, messages: List[BaseMessage]) -> str:
        """Generate mock response for development."""
        import random

        mock_responses = [
            "Based on the patterns, I recommend grouping: WORD1, WORD2, WORD3, WORD4. "
            "These words share a common theme of musical instruments.",
            "I suggest trying: WORD5, WORD6, WORD7, WORD8. " "These appear to be related to sports equipment.",
            "Consider this grouping: WORD9, WORD10, WORD11, WORD12. "
            "These words all relate to types of weather phenomena.",
            "My recommendation is: WORD13, WORD14, WORD15, WORD16. " "These are all examples of kitchen utensils.",
        ]

        return random.choice(mock_responses)


class ClaudeModel(BaseLLMModel):
    """Anthropic Claude model implementation."""

    def __init__(self, config: LLMConfig):
        """Initialize Claude model."""
        super().__init__(config)

        # Get API key from config or environment
        api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("Anthropic API key not provided. Using mock mode.")
            self._mock_mode = True
            return

        self._mock_mode = False
        try:
            # Map our model names to Claude's naming convention
            model_mapping = {"claude-3-sonnet": "claude-3-sonnet-20240229", "claude-3-haiku": "claude-3-haiku-20240307"}

            model_name = model_mapping.get(config.provider.value, config.provider.value)

            self._model = ChatAnthropic(
                model=model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                anthropic_api_key=api_key,
                **config.extra_params,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Claude model: {e}")
            self._mock_mode = True

    async def generate_response(self, messages: List[BaseMessage], **kwargs) -> str:
        """Generate response using Claude model."""
        if self._mock_mode:
            return await self._mock_response(messages)

        try:
            response = await self._model.agenerate([messages])
            return response.generations[0][0].text.strip()
        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            return await self._mock_response(messages)

    def get_model_info(self) -> Dict[str, Any]:
        """Get Claude model information."""
        return {
            "provider": "Anthropic",
            "model": self.config.provider.value,
            "mock_mode": self._mock_mode,
            "config": self.config.to_dict(),
        }

    async def _mock_response(self, messages: List[BaseMessage]) -> str:
        """Generate mock response for development."""
        import random

        mock_responses = [
            "Looking at the available words, I believe these four form a coherent group: "
            "WORD1, WORD2, WORD3, WORD4. They all relate to types of transportation.",
            "I recommend grouping: WORD5, WORD6, WORD7, WORD8. "
            "These words are connected by their association with cooking methods.",
            "Consider this combination: WORD9, WORD10, WORD11, WORD12. "
            "They share the common theme of clothing items.",
            "My analysis suggests: WORD13, WORD14, WORD15, WORD16. " "These are all types of architectural features.",
        ]

        return random.choice(mock_responses)


class MockModel(BaseLLMModel):
    """Mock model for testing and development."""

    def __init__(self, config: LLMConfig):
        """Initialize mock model."""
        super().__init__(config)
        self._mock_mode = True

    async def generate_response(self, messages: List[BaseMessage], **kwargs) -> str:
        """Generate mock response."""
        import random
        import asyncio

        # Simulate API delay
        await asyncio.sleep(random.uniform(0.5, 2.0))

        mock_responses = [
            "I recommend trying these four words together: APPLE, ORANGE, BANANA, GRAPE. "
            "These are all types of fruit that are commonly found in grocery stores.",
            "Consider this grouping: PIANO, GUITAR, VIOLIN, DRUMS. "
            "These are all musical instruments used in various genres of music.",
            "I suggest: RED, BLUE, GREEN, YELLOW. " "These are all primary and secondary colors in the color spectrum.",
            "Try grouping: DOG, CAT, BIRD, FISH. "
            "These are all common household pets that people keep as companions.",
        ]

        return random.choice(mock_responses)

    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information."""
        return {"provider": "Mock", "model": "mock-model", "mock_mode": True, "config": self.config.to_dict()}


class LLMModelFactory:
    """Factory for creating LLM models."""

    # Default configurations for each provider
    DEFAULT_CONFIGS = {
        LLMProvider.OPENAI_GPT4: LLMConfig(
            provider=LLMProvider.OPENAI_GPT4, temperature=0.7, max_tokens=500, top_p=0.9
        ),
        LLMProvider.OPENAI_GPT35_TURBO: LLMConfig(
            provider=LLMProvider.OPENAI_GPT35_TURBO, temperature=0.8, max_tokens=400, top_p=0.9
        ),
        LLMProvider.CLAUDE_3_SONNET: LLMConfig(
            provider=LLMProvider.CLAUDE_3_SONNET, temperature=0.6, max_tokens=500, top_p=0.9
        ),
        LLMProvider.CLAUDE_3_HAIKU: LLMConfig(
            provider=LLMProvider.CLAUDE_3_HAIKU, temperature=0.7, max_tokens=400, top_p=0.9
        ),
        LLMProvider.MOCK: LLMConfig(provider=LLMProvider.MOCK, temperature=0.7, max_tokens=500),
    }

    @classmethod
    def create_model(self, provider: Union[LLMProvider, str], config: Optional[LLMConfig] = None) -> BaseLLMModel:
        """
        Create an LLM model instance.

        Args:
            provider: LLM provider enum or string
            config: Optional custom configuration

        Returns:
            LLM model instance

        Raises:
            ValueError: If provider is not supported
        """
        if isinstance(provider, str):
            try:
                provider = LLMProvider(provider)
            except ValueError:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        # Use provided config or default
        if config is None:
            config = self.DEFAULT_CONFIGS[provider]

        # Create model based on provider
        if provider in [LLMProvider.OPENAI_GPT4, LLMProvider.OPENAI_GPT35_TURBO]:
            return OpenAIModel(config)
        elif provider in [LLMProvider.CLAUDE_3_SONNET, LLMProvider.CLAUDE_3_HAIKU]:
            return ClaudeModel(config)
        elif provider == LLMProvider.MOCK:
            return MockModel(config)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Get list of supported provider names."""
        return [provider.value for provider in LLMProvider]

    @classmethod
    def get_default_config(cls, provider: Union[LLMProvider, str]) -> LLMConfig:
        """
        Get default configuration for a provider.

        Args:
            provider: LLM provider enum or string

        Returns:
            Default configuration for the provider
        """
        if isinstance(provider, str):
            provider = LLMProvider(provider)

        return cls.DEFAULT_CONFIGS[provider]


# Convenience function for creating models
def create_llm_model(provider: Union[LLMProvider, str], config: Optional[LLMConfig] = None) -> BaseLLMModel:
    """
    Convenience function to create an LLM model.

    Args:
        provider: LLM provider enum or string
        config: Optional custom configuration

    Returns:
        LLM model instance
    """
    return LLMModelFactory.create_model(provider, config)


# Export message classes for convenience
__all__ = [
    "LLMProvider",
    "LLMConfig",
    "BaseLLMModel",
    "OpenAIModel",
    "ClaudeModel",
    "MockModel",
    "LLMModelFactory",
    "create_llm_model",
    "HumanMessage",
    "SystemMessage",
    "AIMessage",
    "BaseMessage",
]
