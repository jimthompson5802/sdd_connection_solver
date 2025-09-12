"""LLM integration module for NYT Connections Puzzle Assistant."""

from .model_factory import (
    LLMProvider,
    LLMConfig,
    BaseLLMModel,
    LLMModelFactory,
    create_llm_model,
    HumanMessage,
    SystemMessage,
    AIMessage,
    BaseMessage,
)
from .prompt_templates import (
    PromptType,
    PromptTemplate,
    PromptTemplateManager,
    template_manager,
    get_prompt_for_context,
    register_custom_template,
)
from .recommendation_engine import RecommendationEngine, recommendation_engine, generate_context_aware_recommendation

__all__ = [
    "LLMProvider",
    "LLMConfig",
    "BaseLLMModel",
    "LLMModelFactory",
    "create_llm_model",
    "HumanMessage",
    "SystemMessage",
    "AIMessage",
    "BaseMessage",
    "PromptType",
    "PromptTemplate",
    "PromptTemplateManager",
    "template_manager",
    "get_prompt_for_context",
    "register_custom_template",
    "RecommendationEngine",
    "recommendation_engine",
    "generate_context_aware_recommendation",
]
