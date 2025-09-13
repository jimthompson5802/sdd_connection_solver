"""
Dynamic prompt template system with context injection.

This module provides a flexible prompting system for generating context-aware
AI recommendations for the NYT Connections puzzle game.
"""

import textwrap
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

from ..models.ai_context import AIRecommendationContext
from ..models.group import Group
from ..models.one_away_group import OneAwayGroup


class PromptType(Enum):
    """Types of prompts for different recommendation scenarios."""

    INITIAL = "initial"  # First recommendation with no context
    CONTEXT_AWARE = "context_aware"  # With previous attempts and feedback
    ONE_AWAY_FOCUSED = "one_away_focused"  # Focus on one-away learning
    FINAL_ATTEMPT = "final_attempt"  # Last chance recommendation


@dataclass
class PromptTemplate:
    """Template for generating AI prompts."""

    name: str
    prompt_type: PromptType
    system_message: str
    user_template: str
    variables: List[str]
    description: str

    def render(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Render the template with provided context.

        Args:
            context: Dictionary of variables to inject into template

        Returns:
            Dictionary with 'system' and 'user' messages

        Raises:
            ValueError: If required variables are missing
        """
        # Check for required variables
        missing_vars = set(self.variables) - set(context.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        # Render templates
        system_msg = self.system_message.format(**context)
        user_msg = self.user_template.format(**context)

        return {"system": textwrap.dedent(system_msg).strip(), "user": textwrap.dedent(user_msg).strip()}


class PromptTemplateManager:
    """Manages prompt templates for different scenarios."""

    def __init__(self):
        """Initialize with default templates."""
        self.templates: Dict[str, PromptTemplate] = {}
        self._register_default_templates()

    def register_template(self, template: PromptTemplate) -> None:
        """
        Register a new prompt template.

        Args:
            template: PromptTemplate to register
        """
        self.templates[template.name] = template

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a template by name.

        Args:
            name: Template name

        Returns:
            PromptTemplate if found, None otherwise
        """
        return self.templates.get(name)

    def list_templates(self) -> List[str]:
        """Get list of available template names."""
        """Get list of available template names."""
        # Return the keys of the registered templates as a list
        return list(self.templates.keys())

    def generate_prompt(
        self, template_name: str, ai_context: AIRecommendationContext, **extra_context
    ) -> Dict[str, str]:
        """
        Generate a prompt using specified template and AI context.

        Args:
            template_name: Name of template to use
            ai_context: AI recommendation context
            **extra_context: Additional context variables

        Returns:
            Dictionary with rendered system and user messages

        Raises:
            ValueError: If template not found or context invalid
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Build context from AI context and extra variables
        context = self._build_context_variables(ai_context)
        context.update(extra_context)

        return template.render(context)

    def select_template(self, ai_context: AIRecommendationContext) -> str:
        """
        Automatically select appropriate template based on context.

        Args:
            ai_context: AI recommendation context

        Returns:
            Name of selected template
        """
        # No previous attempts - use initial template
        if not ai_context.incorrect_groups and not ai_context.one_away_groups:
            return "initial_recommendation"

        # Has one-away attempts - focus on learning
        if ai_context.one_away_groups:
            return "one_away_focused"

        # Final attempt scenario (3 incorrect attempts)
        if len(ai_context.incorrect_groups) >= 3:
            return "final_attempt"

        # General context-aware recommendation
        return "context_aware_recommendation"

    def _build_context_variables(self, ai_context: AIRecommendationContext) -> Dict[str, Any]:
        """
        Build context variables from AI context.

        Args:
            ai_context: AI recommendation context

        Returns:
            Dictionary of context variables
        """
        return {
            "remaining_words": ", ".join(ai_context.remaining_words),
            "remaining_words_list": ai_context.remaining_words,
            "words_count": len(ai_context.remaining_words),
            "solved_groups": self._format_solved_groups(ai_context.solved_groups),
            "solved_count": len(ai_context.solved_groups),
            "incorrect_attempts": self._format_incorrect_attempts(ai_context.incorrect_groups),
            "incorrect_count": len(ai_context.incorrect_groups),
            "one_away_attempts": self._format_one_away_attempts(ai_context.one_away_groups),
            "one_away_count": len(ai_context.one_away_groups),
            "has_previous_attempts": bool(ai_context.incorrect_groups or ai_context.one_away_groups),
            "attempt_number": len(ai_context.incorrect_groups) + len(ai_context.one_away_groups) + 1,
        }

    def _format_solved_groups(self, groups: List[Group]) -> str:
        """Format solved groups for prompt inclusion."""
        if not groups:
            return "None yet"

        formatted = []
        for group in groups:
            formatted.append(f"- {group.theme}: {', '.join(group.words)}")

        return "\n".join(formatted)

    def _format_incorrect_attempts(self, groups: List[List[str]]) -> str:
        """Format incorrect attempts for prompt inclusion."""
        if not groups:
            return "None"

        formatted = []
        for i, words in enumerate(groups, 1):
            formatted.append(f"Attempt {i}: {', '.join(words)}")

        return "\n".join(formatted)

    def _format_one_away_attempts(self, groups: List[OneAwayGroup]) -> str:
        """Format one-away attempts for prompt inclusion."""
        if not groups:
            return "None"

        formatted = []
        for i, group in enumerate(groups, 1):
            words_str = ", ".join(group.words)
            formatted.append(f"One-away attempt {i}: {words_str} (close to correct group)")

        return "\n".join(formatted)

    def _register_default_templates(self) -> None:
        """Register default prompt templates."""

        # Initial recommendation template
        initial_template = PromptTemplate(
            name="initial_recommendation",
            prompt_type=PromptType.INITIAL,
            system_message="""
            You are an expert at solving NYT Connections puzzles. Your task is to identify 
            groups of 4 words that share a common theme or connection.
            
            Rules:
            - Each group must contain exactly 4 words
            - Words can only be used once
            - Themes can be literal (e.g., "Types of Birds") or more abstract
            - Some themes may involve wordplay, puns, or cultural references
            - Always provide your reasoning for the grouping
            
            Response format:
            Provide exactly 4 words followed by a clear explanation of their connection.
            """,
            user_template="""
            Here are the 16 words from the puzzle:
            {remaining_words}
            
            Please recommend 4 words that you believe form a group and explain why.
            """,
            variables=["remaining_words"],
            description="Initial recommendation with no previous context",
        )

        # Context-aware recommendation template
        context_aware_template = PromptTemplate(
            name="context_aware_recommendation",
            prompt_type=PromptType.CONTEXT_AWARE,
            system_message="""
            You are an expert at solving NYT Connections puzzles. Your task is to identify 
            groups of 4 words that share a common theme or connection.
            
            You have access to previous attempts and their outcomes. Use this information 
            to avoid repeating mistakes and to refine your understanding of the puzzle.
            
            Rules:
            - Each group must contain exactly 4 words
            - Words can only be used once
            - Avoid groupings that have already been attempted
            - Learn from previous feedback to improve recommendations
            - Always provide your reasoning for the grouping
            
            Response format:
            Provide exactly 4 words followed by a clear explanation of their connection.
            """,
            user_template="""
            Remaining words: {remaining_words}
            
            Previously solved groups:
            {solved_groups}
            
            Previous incorrect attempts:
            {incorrect_attempts}
            
            Previous one-away attempts (very close):
            {one_away_attempts}
            
            Based on this context, please recommend 4 words that form a group and explain why.
            Consider what patterns might connect the remaining words that haven't been tried yet.
            """,
            variables=["remaining_words", "solved_groups", "incorrect_attempts", "one_away_attempts"],
            description="Context-aware recommendation using previous attempts",
        )

        # One-away focused template
        one_away_template = PromptTemplate(
            name="one_away_focused",
            prompt_type=PromptType.ONE_AWAY_FOCUSED,
            system_message="""
            You are an expert at solving NYT Connections puzzles with special focus on 
            "one-away" situations where a previous guess was very close to correct.
            
            When you receive "one-away" feedback, it means 3 out of 4 words were correct
            for a group. Your task is to identify which word to replace and find the 
            correct fourth word.
            
            Rules:
            - Analyze one-away attempts carefully - they contain valuable information
            - Consider which word might be the "outlier" in one-away attempts
            - Look for the missing word that completes the pattern
            - Avoid repeating the exact same 4-word combinations
            
            Response format:
            Provide exactly 4 words followed by explanation focusing on the one-away learning.
            """,
            user_template="""
            Remaining words: {remaining_words}
            
            One-away attempts (3 out of 4 correct):
            {one_away_attempts}
            
            Previously solved groups:
            {solved_groups}
            
            Previous incorrect attempts:
            {incorrect_attempts}
            
            Focus on the one-away attempts. Which word might be the outlier? 
            What word from the remaining set could complete the correct group?
            Please recommend 4 words and explain your reasoning.
            """,
            variables=["remaining_words", "one_away_attempts", "solved_groups", "incorrect_attempts"],
            description="Focused on learning from one-away feedback",
        )

        # Final attempt template
        final_template = PromptTemplate(
            name="final_attempt",
            prompt_type=PromptType.FINAL_ATTEMPT,
            system_message="""
            You are an expert at solving NYT Connections puzzles. This is a critical 
            final attempt situation - you have limited chances remaining.
            
            You must be extremely careful and methodical. Consider all previous attempts
            and feedback to make the most informed decision possible.
            
            Rules:
            - This may be your last chance - be very confident in your choice
            - Thoroughly analyze all previous attempts and patterns
            - Look for subtle connections you might have missed
            - Consider less obvious themes or wordplay
            - Provide detailed reasoning for your choice
            
            Response format:
            Provide exactly 4 words followed by very detailed explanation of the connection.
            """,
            user_template="""
            FINAL ATTEMPT - Be very careful!
            
            Remaining words: {remaining_words}
            
            Previously solved groups:
            {solved_groups}
            
            All previous incorrect attempts:
            {incorrect_attempts}
            
            Previous one-away attempts:
            {one_away_attempts}
            
            This is attempt #{attempt_number}. Analyze all previous attempts carefully.
            What patterns or themes haven't been explored yet? 
            Please make your most confident recommendation with detailed reasoning.
            """,
            variables=["remaining_words", "solved_groups", "incorrect_attempts", "one_away_attempts", "attempt_number"],
            description="Critical final attempt with maximum context analysis",
        )

        # Register all templates
        self.register_template(initial_template)
        self.register_template(context_aware_template)
        self.register_template(one_away_template)
        self.register_template(final_template)


# Global template manager instance
template_manager = PromptTemplateManager()


def get_prompt_for_context(
    ai_context: AIRecommendationContext, template_name: Optional[str] = None, **extra_context
) -> Dict[str, str]:
    """
    Generate appropriate prompt for given AI context.

    Args:
        ai_context: AI recommendation context
        template_name: Optional specific template name (auto-selected if None)
        **extra_context: Additional context variables

    Returns:
        Dictionary with system and user messages
    """
    if template_name is None:
        template_name = template_manager.select_template(ai_context)

    return template_manager.generate_prompt(template_name, ai_context, **extra_context)


def register_custom_template(template: PromptTemplate) -> None:
    """
    Register a custom prompt template.

    Args:
        template: Custom PromptTemplate to register
    """
    template_manager.register_template(template)


# Export main classes and functions
__all__ = [
    "PromptType",
    "PromptTemplate",
    "PromptTemplateManager",
    "template_manager",
    "get_prompt_for_context",
    "register_custom_template",
]
