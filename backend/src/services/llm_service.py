"""LLM recommendation service with context-aware prompting."""

import asyncio
import textwrap
import time
from typing import List, Dict, Any, Tuple

from ..models.ai_context import AIRecommendationContext
from ..models.recommendation import Recommendation


class LLMService:
    """Service for generating AI recommendations using context-aware prompting.

    Provides functionality to:
    - Generate context-aware recommendations using LLM
    - Learn from previous incorrect and one-away evaluations
    - Adapt prompting strategy based on session history
    - Support multiple LLM models (OpenAI, Claude, etc.)
    """

    def __init__(self):
        """Initialize LLM service with default configuration."""
        # Mock LLM responses for development - replace with actual LLM integration
        self._mock_mode = True
        self._model_configs = {
            "gpt-4": {"max_tokens": 500, "temperature": 0.7},
            "gpt-3.5-turbo": {"max_tokens": 400, "temperature": 0.8},
            "claude-3": {"max_tokens": 500, "temperature": 0.6},
        }

    async def generate_recommendation(
        self, session_id: str, context: AIRecommendationContext, llm_model: str = "gpt-4"
    ) -> Recommendation:
        """Generate a context-aware recommendation for the current puzzle state.

        Args:
            session_id: Session requesting the recommendation
            context: Current game context with remaining words and history
            llm_model: LLM model to use for generation

        Returns:
            Generated recommendation with explanation

        Raises:
            ValueError: If context is invalid or model not supported
        """
        if not session_id:
            raise ValueError("session_id is required")
        if len(context.remaining_words) < 4:
            raise ValueError("At least 4 remaining words required for recommendation")
        if llm_model not in self._model_configs:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

        start_time = time.time()

        # Generate context-aware prompt
        prompt = self._build_context_aware_prompt(context)

        # Generate recommendation using LLM (mock for now)
        if self._mock_mode:
            recommended_words, explanation = await self._mock_llm_response(context.remaining_words, context, llm_model)
        else:
            recommended_words, explanation = await self._call_llm_api(prompt, llm_model)

        processing_time = int((time.time() - start_time) * 1000)

        # Create recommendation instance
        recommendation = Recommendation(
            session_id=session_id,
            recommended_words=recommended_words,
            explanation=explanation,
            llm_model=llm_model,
            processing_time_ms=processing_time,
        )

        return recommendation

    def _build_context_aware_prompt(self, context: AIRecommendationContext) -> str:
        """Build context-aware prompt incorporating session history.

        Args:
            context: Game context with history and current state

        Returns:
            Formatted prompt string for LLM
        """
        base_prompt = textwrap.dedent(
            """
        You are an expert at solving NYT Connections puzzles. Your task is to identify a group of 4 words
        that share a common theme or connection from the remaining words.

        REMAINING WORDS: {remaining_words}

        CONTEXT FROM PREVIOUS ATTEMPTS:
        {context_info}

        INSTRUCTIONS:
        1. Identify exactly 4 words that form a coherent group
        2. Provide a clear, concise explanation of their connection
        3. Avoid groups that have been marked as incorrect
        4. Consider the hints from one-away groups to refine your choice
        5. Look for subtle connections (categories, wordplay, themes, etc.)

        Respond with:
        WORDS: [word1, word2, word3, word4]
        EXPLANATION: Brief explanation of the connection
        """
        ).strip()

        # Build context information
        context_info = self._format_context_information(context)

        return base_prompt.format(remaining_words=", ".join(context.remaining_words), context_info=context_info)

    def _format_context_information(self, context: AIRecommendationContext) -> str:
        """Format context information from session history.

        Args:
            context: Game context with history

        Returns:
            Formatted context string
        """
        info_parts = []

        # Add solved groups for reference
        if context.solved_groups:
            solved_info = []
            for group in context.solved_groups:
                solved_info.append(f"✓ {', '.join(group.words)} - {group.theme}")
            info_parts.append("SOLVED GROUPS:\n" + "\n".join(solved_info))

        # Add incorrect attempts to avoid
        if context.incorrect_groups:
            incorrect_info = []
            for group in context.incorrect_groups:
                incorrect_info.append(f"✗ {', '.join(group)}")
            info_parts.append("INCORRECT ATTEMPTS (avoid these):\n" + "\n".join(incorrect_info))

        # Add one-away groups with hints
        if context.one_away_groups:
            oneaway_info = []
            for group in context.one_away_groups:
                hint = f" (hint: {group.correct_connection})" if group.correct_connection else ""
                oneaway_info.append(f"~ {', '.join(group.attempted_words)} - one word wrong{hint}")
            info_parts.append("ONE-AWAY GROUPS (3 words correct, 1 wrong):\n" + "\n".join(oneaway_info))

        return "\n\n".join(info_parts) if info_parts else "No previous context available."

    async def _mock_llm_response(
        self, remaining_words: List[str], context: AIRecommendationContext, llm_model: str
    ) -> Tuple[List[str], str]:
        """Generate mock LLM response for development/testing.

        Args:
            remaining_words: Available words
            context: Game context
            llm_model: Model being simulated

        Returns:
            Tuple of (recommended_words, explanation)
        """
        # Simulate network delay
        await asyncio.sleep(0.1)

        # Simple mock logic - take first 4 words and create explanation
        if len(remaining_words) >= 4:
            recommended_words = remaining_words[:4]
            explanation = f"These words share a thematic connection (mock response from {llm_model})"
        else:
            recommended_words = remaining_words
            explanation = "Using all remaining words as they may form the final group"

        return recommended_words, explanation

    async def _call_llm_api(self, prompt: str, llm_model: str) -> Tuple[List[str], str]:
        """Call actual LLM API to generate recommendation.

        Args:
            prompt: Formatted prompt for LLM
            llm_model: LLM model to use

        Returns:
            Tuple of (recommended_words, explanation)

        Note:
            This is a placeholder for actual LLM API integration.
            In real implementation, would use libraries like openai, anthropic, etc.
        """
        # Placeholder for real LLM API calls
        # Would integrate with OpenAI, Anthropic, or other LLM providers

        # For now, return mock response
        await asyncio.sleep(0.5)  # Simulate API call delay

        return (["word1", "word2", "word3", "word4"], f"Mock API response from {llm_model}")

    def validate_llm_model(self, llm_model: str) -> bool:
        """Validate if LLM model is supported.

        Args:
            llm_model: Model identifier to validate

        Returns:
            True if model is supported, False otherwise
        """
        return llm_model in self._model_configs

    def get_supported_models(self) -> List[str]:
        """Get list of supported LLM models.

        Returns:
            List of supported model identifiers
        """
        return list(self._model_configs.keys())

    def update_model_config(self, llm_model: str, config: Dict[str, Any]) -> bool:
        """Update configuration for a specific LLM model.

        Args:
            llm_model: Model identifier
            config: New configuration parameters

        Returns:
            True if config was updated, False if model not found
        """
        if llm_model in self._model_configs:
            self._model_configs[llm_model].update(config)
            return True
        return False

    def estimate_processing_time(self, llm_model: str, word_count: int) -> int:
        """Estimate processing time for a recommendation request.

        Args:
            llm_model: LLM model to use
            word_count: Number of remaining words

        Returns:
            Estimated processing time in milliseconds
        """
        base_time = {"gpt-4": 1500, "gpt-3.5-turbo": 800, "claude-3": 1200}.get(llm_model, 1000)

        # Add complexity factor based on word count
        complexity_factor = 1 + (word_count - 4) * 0.1

        return int(base_time * complexity_factor)
