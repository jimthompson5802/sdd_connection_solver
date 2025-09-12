"""Unit tests for LLM prompt generation logic."""

import pytest

from src.llm.prompt_templates import (
    PromptTemplate,
    PromptTemplateManager,
    PromptType,
    get_prompt_for_context,
    register_custom_template,
    template_manager,
)
from src.models.ai_context import AIRecommendationContext
from src.models.group import Group
from src.models.one_away_group import OneAwayGroup


class TestPromptTemplate:
    """Test cases for PromptTemplate class."""

    def test_init(self):
        """Test PromptTemplate initialization."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.INITIAL,
            system_message="System: {var1}",
            user_template="User: {var2}",
            variables=["var1", "var2"],
            description="Test template",
        )

        assert template.name == "test_template"
        assert template.prompt_type == PromptType.INITIAL
        assert template.system_message == "System: {var1}"
        assert template.user_template == "User: {var2}"
        assert template.variables == ["var1", "var2"]
        assert template.description == "Test template"

    def test_render_success(self):
        """Test successful template rendering."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.INITIAL,
            system_message="System: {var1}",
            user_template="User: {var2}",
            variables=["var1", "var2"],
            description="Test template",
        )

        context = {"var1": "value1", "var2": "value2"}
        result = template.render(context)

        assert result == {"system": "System: value1", "user": "User: value2"}

    def test_render_with_multiline_and_whitespace(self):
        """Test template rendering with multiline strings and whitespace."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.INITIAL,
            system_message="""
                System message with
                multiple lines and {var1}
            """,
            user_template="""
                User message with
                multiple lines and {var2}
            """,
            variables=["var1", "var2"],
            description="Test template",
        )

        context = {"var1": "value1", "var2": "value2"}
        result = template.render(context)

        # Check that dedent and strip are applied
        assert "System message with\nmultiple lines and value1" in result["system"]
        assert "User message with\nmultiple lines and value2" in result["user"]
        assert not result["system"].startswith(" ")
        assert not result["user"].startswith(" ")

    def test_render_missing_variables(self):
        """Test template rendering with missing variables."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.INITIAL,
            system_message="System: {var1}",
            user_template="User: {var2}",
            variables=["var1", "var2"],
            description="Test template",
        )

        context = {"var1": "value1"}  # Missing var2

        with pytest.raises(ValueError, match="Missing required variables: {'var2'}"):
            template.render(context)

    def test_render_extra_variables(self):
        """Test template rendering with extra variables (should work)."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.INITIAL,
            system_message="System: {var1}",
            user_template="User: {var2}",
            variables=["var1", "var2"],
            description="Test template",
        )

        context = {"var1": "value1", "var2": "value2", "extra": "extra_value"}
        result = template.render(context)

        assert result == {"system": "System: value1", "user": "User: value2"}


class TestPromptTemplateManager:
    """Test cases for PromptTemplateManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PromptTemplateManager()

    def test_init_with_default_templates(self):
        """Test manager initialization includes default templates."""
        templates = self.manager.list_templates()

        assert "initial_recommendation" in templates
        assert "context_aware_recommendation" in templates
        assert "one_away_focused" in templates
        assert "final_attempt" in templates
        assert len(templates) == 4

    def test_register_template(self):
        """Test registering a new template."""
        template = PromptTemplate(
            name="custom_template",
            prompt_type=PromptType.INITIAL,
            system_message="Custom system",
            user_template="Custom user",
            variables=[],
            description="Custom template",
        )

        self.manager.register_template(template)

        assert "custom_template" in self.manager.list_templates()
        assert self.manager.get_template("custom_template") == template

    def test_get_template_exists(self):
        """Test getting existing template."""
        template = self.manager.get_template("initial_recommendation")

        assert template is not None
        assert template.name == "initial_recommendation"
        assert template.prompt_type == PromptType.INITIAL

    def test_get_template_not_exists(self):
        """Test getting non-existent template."""
        template = self.manager.get_template("nonexistent")

        assert template is None

    def test_list_templates(self):
        """Test listing all templates."""
        templates = self.manager.list_templates()

        assert isinstance(templates, list)
        assert len(templates) >= 4  # At least the default templates
        assert "initial_recommendation" in templates

    def test_generate_prompt_success(self):
        """Test successful prompt generation."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        result = self.manager.generate_prompt("initial_recommendation", ai_context)

        assert "system" in result
        assert "user" in result
        assert "apple, banana, cherry, date" in result["user"]

    def test_generate_prompt_template_not_found(self):
        """Test prompt generation with non-existent template."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        with pytest.raises(ValueError, match="Template 'nonexistent' not found"):
            self.manager.generate_prompt("nonexistent", ai_context)

    def test_select_template_initial(self):
        """Test template selection for initial recommendation."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        template_name = self.manager.select_template(ai_context)

        assert template_name == "initial_recommendation"

    def test_select_template_context_aware(self):
        """Test template selection for context-aware recommendation."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[["word1", "word2", "word3", "word4"]],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        template_name = self.manager.select_template(ai_context)

        assert template_name == "context_aware_recommendation"

    def test_select_template_one_away_focused(self):
        """Test template selection for one-away focused recommendation."""
        one_away_group = OneAwayGroup(words=["apple", "banana", "cherry", "grape"], explanation="One away from correct group")
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[one_away_group],
        )

        template_name = self.manager.select_template(ai_context)

        assert template_name == "one_away_focused"

    def test_select_template_final_attempt(self):
        """Test template selection for final attempt."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[
                ["word1", "word2", "word3", "word4"],
                ["word5", "word6", "word7", "word8"],
                ["word9", "word10", "word11", "word12"],
            ],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        template_name = self.manager.select_template(ai_context)

        assert template_name == "final_attempt"

    def test_build_context_variables_minimal(self):
        """Test building context variables with minimal AI context."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        context = self.manager._build_context_variables(ai_context)

        assert context["remaining_words"] == "apple, banana, cherry, date"
        assert context["remaining_words_list"] == ["apple", "banana", "cherry", "date"]
        assert context["words_count"] == 4
        assert context["solved_groups"] == "None yet"
        assert context["solved_count"] == 0
        assert context["incorrect_attempts"] == "None"
        assert context["incorrect_count"] == 0
        assert context["one_away_attempts"] == "None"
        assert context["one_away_count"] == 0
        assert context["has_previous_attempts"] is False
        assert context["attempt_number"] == 1

    def test_build_context_variables_full(self):
        """Test building context variables with full AI context."""
        solved_group = Group(words=["red", "blue", "green", "yellow"], theme="Colors", difficulty="yellow")
        one_away_group = OneAwayGroup(words=["apple", "banana", "cherry", "grape"], explanation="One away from correct group")

        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[solved_group],
            incorrect_groups=[["word1", "word2", "word3", "word4"]],
            one_away_groups=[one_away_group],
        )

        context = self.manager._build_context_variables(ai_context)

        assert context["remaining_words"] == "apple, banana, cherry, date"
        assert context["words_count"] == 4
        assert "Colors: red, blue, green, yellow" in context["solved_groups"]
        assert context["solved_count"] == 1
        assert "Attempt 1: word1, word2, word3, word4" in context["incorrect_attempts"]
        assert context["incorrect_count"] == 1
        assert "One-away attempt 1: apple, banana, cherry, grape" in context["one_away_attempts"]
        assert context["one_away_count"] == 1
        assert context["has_previous_attempts"] is True
        assert context["attempt_number"] == 3  # 1 incorrect + 1 one-away + 1 new = 3

    def test_format_solved_groups_empty(self):
        """Test formatting empty solved groups."""
        result = self.manager._format_solved_groups([])

        assert result == "None yet"

    def test_format_solved_groups_multiple(self):
        """Test formatting multiple solved groups."""
        groups = [
            Group(words=["red", "blue", "green", "yellow"], theme="Colors", difficulty="yellow"),
            Group(words=["cat", "dog", "bird", "fish"], theme="Animals", difficulty="medium"),
        ]

        result = self.manager._format_solved_groups(groups)

        assert "- Colors: red, blue, green, yellow" in result
        assert "- Animals: cat, dog, bird, fish" in result

    def test_format_incorrect_attempts_empty(self):
        """Test formatting empty incorrect attempts."""
        result = self.manager._format_incorrect_attempts([])

        assert result == "None"

    def test_format_incorrect_attempts_multiple(self):
        """Test formatting multiple incorrect attempts."""
        attempts = [
            ["word1", "word2", "word3", "word4"],
            ["word5", "word6", "word7", "word8"],
        ]

        result = self.manager._format_incorrect_attempts(attempts)

        assert "Attempt 1: word1, word2, word3, word4" in result
        assert "Attempt 2: word5, word6, word7, word8" in result

    def test_format_one_away_attempts_empty(self):
        """Test formatting empty one-away attempts."""
        result = self.manager._format_one_away_attempts([])

        assert result == "None"

    def test_format_one_away_attempts_multiple(self):
        """Test formatting multiple one-away attempts."""
        attempts = [
            OneAwayGroup(words=["apple", "banana", "cherry", "grape"], explanation="One away from correct group"),
            OneAwayGroup(words=["cat", "dog", "bird", "snake"], explanation="One away from correct group"),
        ]

        result = self.manager._format_one_away_attempts(attempts)

        assert "One-away attempt 1: apple, banana, cherry, grape (close to correct group)" in result
        assert "One-away attempt 2: cat, dog, bird, snake (close to correct group)" in result


class TestPromptGeneration:
    """Test cases for high-level prompt generation functions."""

    def test_get_prompt_for_context_auto_select(self):
        """Test automatic template selection and prompt generation."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        result = get_prompt_for_context(ai_context)

        assert "system" in result
        assert "user" in result
        assert "apple, banana, cherry, date" in result["user"]

    def test_get_prompt_for_context_specific_template(self):
        """Test prompt generation with specific template."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        result = get_prompt_for_context(ai_context, template_name="context_aware_recommendation")

        assert "system" in result
        assert "user" in result
        # Should use context-aware template even though context suggests initial

    def test_get_prompt_for_context_extra_context(self):
        """Test prompt generation with extra context variables."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        # Custom template that uses extra variables
        custom_template = PromptTemplate(
            name="custom_with_extra",
            prompt_type=PromptType.INITIAL,
            system_message="System",
            user_template="Words: {remaining_words}, Extra: {extra_var}",
            variables=["remaining_words", "extra_var"],
            description="Custom template with extra var",
        )
        template_manager.register_template(custom_template)

        result = get_prompt_for_context(ai_context, template_name="custom_with_extra", extra_var="extra_value")

        assert "Extra: extra_value" in result["user"]

    def test_register_custom_template_function(self):
        """Test registering custom template via function."""
        custom_template = PromptTemplate(
            name="test_custom_function",
            prompt_type=PromptType.INITIAL,
            system_message="Custom system",
            user_template="Custom user",
            variables=[],
            description="Custom template via function",
        )

        register_custom_template(custom_template)

        # Should be available in global template manager
        template = template_manager.get_template("test_custom_function")
        assert template is not None
        assert template.name == "test_custom_function"

    def test_default_templates_completeness(self):
        """Test that all default templates are properly configured."""
        # Test all default templates can be retrieved and have expected properties
        default_templates = [
            ("initial_recommendation", PromptType.INITIAL),
            ("context_aware_recommendation", PromptType.CONTEXT_AWARE),
            ("one_away_focused", PromptType.ONE_AWAY_FOCUSED),
            ("final_attempt", PromptType.FINAL_ATTEMPT),
        ]

        for template_name, expected_type in default_templates:
            template = template_manager.get_template(template_name)
            assert template is not None, f"Template {template_name} not found"
            assert template.prompt_type == expected_type
            assert template.variables  # Should have some variables
            assert template.system_message  # Should have system message
            assert template.user_template  # Should have user template

    def test_template_variable_consistency(self):
        """Test that all default templates have consistent variable usage."""
        ai_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[["word1", "word2", "word3", "word4"]],
            one_away_groups=[OneAwayGroup(words=["apple", "banana", "cherry", "grape"], explanation="One away from correct group")],
        )

        # Test that all default templates can be rendered without errors
        for template_name in template_manager.list_templates():
            try:
                result = get_prompt_for_context(ai_context, template_name=template_name)
                assert "system" in result
                assert "user" in result
                assert result["system"]  # Should not be empty
                assert result["user"]  # Should not be empty
            except Exception as e:
                pytest.fail(f"Template {template_name} failed to render: {e}")

    def test_template_context_sensitivity(self):
        """Test that templates adapt to different context scenarios."""
        # Test initial context (no previous attempts)
        initial_context = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        # Test context with attempts
        context_with_attempts = AIRecommendationContext(
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[["word1", "word2", "word3", "word4"]],
            one_away_groups=[],
            llm_prompt_template="default_template",        )

        initial_prompt = get_prompt_for_context(initial_context)
        context_prompt = get_prompt_for_context(context_with_attempts)

        # Different contexts should produce different prompts
        assert initial_prompt != context_prompt
