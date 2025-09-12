"""
Context-aware recommendation generation with one-away learning.

This module provides the core recommendation engine that combines LLM models
with prompt templates to generate intelligent recommendations based on game context.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any

from ..models.ai_context import AIRecommendationContext
from ..models.recommendation import Recommendation
from .model_factory import create_llm_model, LLMProvider, BaseLLMModel, HumanMessage, SystemMessage
from .prompt_templates import get_prompt_for_context


logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Advanced recommendation engine with context-aware learning.

    This engine integrates LLM models with dynamic prompt templates to generate
    intelligent recommendations that learn from previous attempts and feedback.
    """

    def __init__(self, default_provider: str = "mock"):
        """
        Initialize recommendation engine.

        Args:
            default_provider: Default LLM provider to use
        """
        self.default_provider = default_provider
        self._model_cache: Dict[str, BaseLLMModel] = {}

        # Configuration for different attempt scenarios
        self.attempt_configs = {
            "initial": {"temperature": 0.7, "max_tokens": 300},
            "context_aware": {"temperature": 0.6, "max_tokens": 400},
            "one_away_focused": {"temperature": 0.5, "max_tokens": 350},
            "final_attempt": {"temperature": 0.4, "max_tokens": 500},
        }

    async def generate_recommendation(
        self,
        session_id: str,
        ai_context: AIRecommendationContext,
        llm_model: str = None,
        template_name: Optional[str] = None,
        **kwargs,
    ) -> Recommendation:
        """
        Generate context-aware recommendation for current puzzle state.

        Args:
            session_id: Session requesting the recommendation
            ai_context: Current game context with remaining words and history
            llm_model: LLM model to use (defaults to engine's default)
            template_name: Specific template to use (auto-selected if None)
            **kwargs: Additional parameters for generation

        Returns:
            Generated recommendation with explanation

        Raises:
            ValueError: If context is invalid or generation fails
        """
        start_time = time.time()

        # Validate input
        if not session_id:
            raise ValueError("session_id is required")
        if len(ai_context.remaining_words) < 4:
            raise ValueError("At least 4 remaining words required for recommendation")

        # Use default model if not specified
        model_name = llm_model or self.default_provider

        try:
            # Get or create LLM model
            model = await self._get_model(model_name)

            # Generate context-aware prompt
            prompt_data = get_prompt_for_context(ai_context, template_name)

            # Create messages for LLM
            messages = [SystemMessage(content=prompt_data["system"]), HumanMessage(content=prompt_data["user"])]

            # Generate recommendation
            raw_response = await model.generate_response(messages, **kwargs)

            # Parse and validate response
            recommended_words, explanation = self._parse_llm_response(raw_response, ai_context.remaining_words)

            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)

            # Create recommendation object
            recommendation = Recommendation(
                session_id=session_id,
                recommended_words=recommended_words,
                explanation=explanation,
                llm_model=model_name,
                processing_time_ms=processing_time,
            )

            logger.info(
                f"Generated recommendation for session {session_id}: " f"{recommended_words} in {processing_time}ms"
            )

            return recommendation

        except Exception as e:
            logger.error(f"Failed to generate recommendation: {e}")
            # Generate fallback recommendation
            return await self._generate_fallback_recommendation(session_id, ai_context, model_name, start_time)

    async def generate_batch_recommendations(
        self, session_id: str, ai_context: AIRecommendationContext, count: int = 3, llm_model: str = None
    ) -> List[Recommendation]:
        """
        Generate multiple recommendations for comparison.

        Args:
            session_id: Session requesting recommendations
            ai_context: Current game context
            count: Number of recommendations to generate
            llm_model: LLM model to use

        Returns:
            List of generated recommendations
        """
        tasks = []

        for i in range(count):
            # Use different temperature for variety
            temp_variation = 0.1 * i
            task = self.generate_recommendation(session_id, ai_context, llm_model, temperature=0.7 + temp_variation)
            tasks.append(task)

        recommendations = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed generations
        valid_recommendations = [r for r in recommendations if isinstance(r, Recommendation)]

        return valid_recommendations

    async def _get_model(self, model_name: str) -> BaseLLMModel:
        """
        Get or create LLM model instance.

        Args:
            model_name: Name of the model to get

        Returns:
            LLM model instance
        """
        if model_name not in self._model_cache:
            try:
                provider = LLMProvider(model_name)
                self._model_cache[model_name] = create_llm_model(provider)
            except ValueError:
                logger.warning(f"Unknown model {model_name}, using mock model")
                self._model_cache[model_name] = create_llm_model(LLMProvider.MOCK)

        return self._model_cache[model_name]

    def _parse_llm_response(self, response: str, available_words: List[str]) -> Tuple[List[str], str]:
        """
        Parse LLM response to extract recommended words and explanation.

        Args:
            response: Raw LLM response
            available_words: List of available words for validation

        Returns:
            Tuple of (recommended_words, explanation)

        Raises:
            ValueError: If parsing fails or words are invalid
        """
        lines = response.strip().split("\n")

        # Try to find 4 words in the response
        recommended_words = []
        explanation_parts = []

        # Look for words in the response
        for line in lines:
            words_in_line = []

            # Split by common separators and check against available words
            potential_words = line.replace(",", " ").replace(":", " ").split()

            for word in potential_words:
                clean_word = word.strip('.,!?;:"()[]{}').upper()
                if clean_word in [w.upper() for w in available_words]:
                    words_in_line.append(clean_word)

            # If we found words, add them to recommendations
            if words_in_line:
                recommended_words.extend(words_in_line)
            else:
                # This line might be explanation
                explanation_parts.append(line.strip())

        # Take first 4 unique words found
        unique_words = []
        for word in recommended_words:
            if word not in unique_words and len(unique_words) < 4:
                # Find original case from available words
                for available in available_words:
                    if available.upper() == word.upper():
                        unique_words.append(available)
                        break

        # If we don't have 4 words, try fallback parsing
        if len(unique_words) != 4:
            unique_words = self._fallback_word_extraction(response, available_words)

        # Build explanation
        explanation = " ".join(explanation_parts).strip()
        if not explanation:
            explanation = f"Recommended grouping: {', '.join(unique_words)}"

        return unique_words, explanation

    def _fallback_word_extraction(self, response: str, available_words: List[str]) -> List[str]:
        """
        Fallback method to extract words from response.

        Args:
            response: Raw LLM response
            available_words: Available words for selection

        Returns:
            List of 4 words (random selection if parsing fails)
        """
        import re
        import random

        # Try more aggressive pattern matching
        found_words = []

        # Convert available words to uppercase for matching
        available_upper = [w.upper() for w in available_words]

        # Look for any occurrence of available words in the response
        response_upper = response.upper()
        for i, word in enumerate(available_words):
            if word.upper() in response_upper and word not in found_words:
                found_words.append(word)
                if len(found_words) == 4:
                    break

        # If still not enough words, randomly select from available
        if len(found_words) < 4:
            remaining_words = [w for w in available_words if w not in found_words]
            needed = 4 - len(found_words)
            found_words.extend(random.sample(remaining_words, min(needed, len(remaining_words))))

        return found_words[:4]

    async def _generate_fallback_recommendation(
        self, session_id: str, ai_context: AIRecommendationContext, model_name: str, start_time: float
    ) -> Recommendation:
        """
        Generate fallback recommendation when main generation fails.

        Args:
            session_id: Session ID
            ai_context: AI context
            model_name: Model name that was attempted
            start_time: Start time for processing calculation

        Returns:
            Fallback recommendation
        """
        import random

        # Select 4 random words from available
        recommended_words = random.sample(ai_context.remaining_words, 4)

        processing_time = int((time.time() - start_time) * 1000)

        return Recommendation(
            session_id=session_id,
            recommended_words=recommended_words,
            explanation="Generated fallback recommendation due to processing error.",
            llm_model=f"{model_name}-fallback",
            processing_time_ms=processing_time,
        )

    def get_recommendation_confidence(
        self, recommendation: Recommendation, ai_context: AIRecommendationContext
    ) -> float:
        """
        Calculate confidence score for a recommendation.

        Args:
            recommendation: Generated recommendation
            ai_context: AI context used for generation

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence

        # Factors that increase confidence
        if len(recommendation.explanation) > 50:
            confidence += 0.1  # Detailed explanation

        if recommendation.processing_time_ms < 2000:
            confidence += 0.1  # Quick generation suggests confidence

        if len(ai_context.one_away_groups) > 0:
            confidence += 0.2  # Learning from one-away feedback

        # Factors that decrease confidence
        if len(ai_context.incorrect_groups) > 2:
            confidence -= 0.2  # Many failed attempts

        if "fallback" in recommendation.llm_model:
            confidence = 0.1  # Low confidence for fallback

        return max(0.0, min(1.0, confidence))

    def analyze_recommendation_quality(
        self, recommendation: Recommendation, ai_context: AIRecommendationContext
    ) -> Dict[str, Any]:
        """
        Analyze the quality of a generated recommendation.

        Args:
            recommendation: Generated recommendation
            ai_context: AI context used for generation

        Returns:
            Dictionary with quality analysis
        """
        analysis = {
            "confidence": self.get_recommendation_confidence(recommendation, ai_context),
            "novelty": self._calculate_novelty(recommendation, ai_context),
            "processing_time": recommendation.processing_time_ms,
            "explanation_length": len(recommendation.explanation),
            "uses_context": self._uses_context_effectively(recommendation, ai_context),
        }

        # Overall quality score
        analysis["quality_score"] = (
            analysis["confidence"] * 0.4
            + analysis["novelty"] * 0.3
            + (1.0 if analysis["processing_time"] < 3000 else 0.5) * 0.2
            + (1.0 if analysis["uses_context"] else 0.0) * 0.1
        )

        return analysis

    def _calculate_novelty(self, recommendation: Recommendation, ai_context: AIRecommendationContext) -> float:
        """Calculate how novel/different the recommendation is from previous attempts."""
        recommended_set = set(recommendation.recommended_words)

        # Check against previous incorrect attempts
        for incorrect_group in ai_context.incorrect_groups:
            incorrect_set = set(incorrect_group)
            overlap = len(recommended_set.intersection(incorrect_set))
            if overlap >= 3:  # Too similar to previous attempt
                return 0.2

        # Check against one-away attempts
        for one_away in ai_context.one_away_groups:
            one_away_set = set(one_away.attempted_words)
            if recommended_set == one_away_set:  # Exact repeat
                return 0.1

        return 1.0  # Novel recommendation

    def _uses_context_effectively(self, recommendation: Recommendation, ai_context: AIRecommendationContext) -> bool:
        """Check if the recommendation appears to use context effectively."""
        if not ai_context.incorrect_groups and not ai_context.one_away_groups:
            return True  # No context to use

        # Check if explanation mentions learning or avoiding previous attempts
        explanation_lower = recommendation.explanation.lower()
        context_indicators = [
            "previous",
            "avoid",
            "different",
            "instead",
            "learned",
            "unlike",
            "considering",
            "based on",
            "attempt",
        ]

        return any(indicator in explanation_lower for indicator in context_indicators)


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()


async def generate_context_aware_recommendation(
    session_id: str, ai_context: AIRecommendationContext, llm_model: str = None, **kwargs
) -> Recommendation:
    """
    Convenience function to generate context-aware recommendation.

    Args:
        session_id: Session requesting recommendation
        ai_context: AI context with game state
        llm_model: Optional LLM model to use
        **kwargs: Additional generation parameters

    Returns:
        Generated recommendation
    """
    return await recommendation_engine.generate_recommendation(session_id, ai_context, llm_model, **kwargs)


# Export main classes and functions
__all__ = ["RecommendationEngine", "recommendation_engine", "generate_context_aware_recommendation"]
