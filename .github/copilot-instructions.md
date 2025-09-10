# sdd_connection_solver Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-09-08

## Active Technologies
-  +  (001-nyt-connections-puzzle)

## Project Structure
```
src/
tests/
```


## Code Style
1. **Python Style**: 
   - Follow PEP 8 conventions for Python code
   - Allow line length up to 120 characters
   - Use PascalCase for class names (e.g., `SentimentAnalyzer`)
   - Use snake_case for variables and functions (e.g., `analyze_text`, `sentiment_score`)

2. **Type Hints**: Include type annotations for function parameters and return values

3. **Documentation**: 
   - Add docstrings to all functions and classes
   - Use Google-style docstrings with Args and Returns sections

4. **Error Handling**: 
   - Use try/except blocks for error handling
   - Provide descriptive error messages

5. **Async Programming**:
   - Use asyncio for asynchronous operations
   - Employ async context managers with AsyncExitStack for resource cleanup

6. **Command-line Interfaces**:
   - Use argparse for processing command-line arguments
   - Provide helpful descriptions for all arguments

7. **Code Organization**:
   - Keep classes focused on a single responsibility
   - Use clear, descriptive variable and function names
   - Group related functionality within classes

8. **LLM Prompt**
   - when a prompt will span muliple lines use the triple quotes `"""` to enclose the prompt text.
   - use `textwrap.dedent` to remove any common leading whitespace.

## Recent Changes
- 001-nyt-connections-puzzle: Added  + 

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->