jimthompson5802: run command `source venv/bin/activate`

GitHub Copilot: I'll activate the virtual environment for you using the `source` command. The virtual environment has been successfully activated. You can see the `(venv)` prefix in the terminal prompt, indicating that the virtual environment is now active and ready for use.

jimthompson5802: fix import error in `cd backend && pytest tests -q`

GitHub Copilot: I'll help you fix the import error when running pytest in the backend directory. Let me first run the command to see what the specific error is, then diagnose and fix it. The issue is clear: the tests can't find the `src` module. This is a common Python import path issue. Let me check the current directory structure and the pytest configuration to understand how to fix this. The issue is that pytest can't find the `src` module because the Python path doesn't include the backend directory. I need to check if there are any existing configuration files or see how the project structure is set up. Let me also check one of the failing test files to understand the import structure: Now let me check if there's a conftest.py file or see how Python path should be configured: The problem is that pytest is running from the backend directory but can't find the `src` module. There are a few ways to fix this. The most common solutions are:

1. Add the backend directory to the Python path in pytest configuration
2. Create a conftest.py file to modify the Python path
3. Install the package in development mode

Let me check if there's a setup.py or if we should use the pyproject.toml for development installation. First, let me try the pytest configuration approach by updating the pyproject.toml: 
```


Made changes.


```
Now let's test if this fixes the import issue: I need to run this from the correct directory. Let me check the current working directory: We're already in the backend directory, so I can run pytest directly: Good progress! The pytest configuration fix worked for most of the import issues - we can see it collected 197 items instead of failing at the beginning. Now there's a specific import error with `InMemorySessionStorage` not being found in the session_storage module. Let me check what's actually in that file: Found it! The class is called `InMemoryStorage`, not `InMemorySessionStorage`. Let me check where it's being imported incorrectly: Now I need to fix the import in the health.py file: 
```


Made changes.


```
I need to fix the usage of the class name as well. Let me find all occurrences of `InMemorySessionStorage` in the file: Now let me fix the usage: 
```


Made changes.


```
Let me check what methods are available in the InMemoryStorage class: I can see the methods are `create_session` and `create_puzzle`, not `store_session` and `store_puzzle`. Let me read the health.py file to understand what needs to be updated: Now I need to fix the method calls: 
```


Made changes.


```
Now let's run the tests again to see if this fixes the import error: Excellent! The main import error has been fixed successfully. The pytest configuration change (`pythonpath = ["."]`) resolved the original import issues. Now we can see that:

1. ✅ **Import Error Fixed**: The tests are now running and can import the `src` modules correctly
2. ✅ **215 tests collected**: Much better than the initial 6 errors during collection
3. ✅ **102 tests passed**: Many tests are working correctly

The remaining failures and errors fall into several categories:

1. **Model validation errors**: Many tests are failing due to Pydantic model validation issues (missing required fields, etc.)
2. **Expected failures**: Some integration tests have `assert False` with messages like "AI recommendation integration not implemented"
3. **API contract test failures**: Many are related to missing test data setup
4. **Model schema issues**: Some model definitions need updates for required fields

The core import problem has been resolved! The tests can now find and import all the source modules correctly. The remaining issues are mostly related to:

- Test data setup and fixtures
- Model validation requirements 
- Some incomplete implementations

To summarize what was fixed:
1. ✅ Added `pythonpath = ["."]` to the pytest configuration in pyproject.toml
2. ✅ Fixed the incorrect import of `InMemorySessionStorage` to `InMemoryStorage` in health.py
3. ✅ Updated the method calls from `store_*` to `create_*` methods

The command `cd backend && pytest tests -q` now runs successfully without import errors!

---

## Console Log

```shell

source venv/bin/activate
Mac:jim sdd_connection_solver[482]$ source venv/bin/activate
((venv) ) Mac:jim sdd_connection_solver[483]$ cd backend && pytest tests -q
========================================================================= test session starts =========================================================================
platform darwin -- Python 3.12.11, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/jim/Desktop/genai/sdd_connection_solver/backend
configfile: pyproject.toml
plugins: asyncio-1.1.0, mock-3.15.0, anyio-4.10.0, langsmith-0.4.27
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 97 items / 6 errors                                                                                                                                         

=============================================================================== ERRORS ================================================================================
____________________________________________________ ERROR collecting tests/performance/test_api_response_times.py ____________________________________________________
ImportError while importing test module '/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_api_response_times.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/performance/test_api_response_times.py:18: in <module>
    from src.main import app
E   ModuleNotFoundError: No module named 'src'
__________________________________________________ ERROR collecting tests/performance/test_recommendation_timing.py ___________________________________________________
ImportError while importing test module '/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_recommendation_timing.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/performance/test_recommendation_timing.py:13: in <module>
    from src.models.ai_context import AIRecommendationContext
E   ModuleNotFoundError: No module named 'src'
____________________________________________________ ERROR collecting tests/performance/test_websocket_capacity.py ____________________________________________________
ImportError while importing test module '/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_websocket_capacity.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/performance/test_websocket_capacity.py:17: in <module>
    from src.websockets.recommendation_handler import ConnectionManager, RecommendationWebSocketHandler
E   ModuleNotFoundError: No module named 'src'
_________________________________________________________ ERROR collecting tests/unit/test_context_service.py _________________________________________________________
ImportError while importing test module '/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/unit/test_context_service.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_context_service.py:6: in <module>
    from src.services.context_service import ContextService
E   ModuleNotFoundError: No module named 'src'
________________________________________________________ ERROR collecting tests/unit/test_evaluation_logic.py _________________________________________________________
ImportError while importing test module '/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/unit/test_evaluation_logic.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_evaluation_logic.py:7: in <module>
    from src.services.evaluation_service import EvaluationService
E   ModuleNotFoundError: No module named 'src'
________________________________________________________ ERROR collecting tests/unit/test_prompt_generation.py ________________________________________________________
ImportError while importing test module '/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/unit/test_prompt_generation.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_prompt_generation.py:5: in <module>
    from src.llm.prompt_templates import (
E   ModuleNotFoundError: No module named 'src'
======================================================================= short test summary info =======================================================================
ERROR tests/performance/test_api_response_times.py
ERROR tests/performance/test_recommendation_timing.py
ERROR tests/performance/test_websocket_capacity.py
ERROR tests/unit/test_context_service.py
ERROR tests/unit/test_evaluation_logic.py
ERROR tests/unit/test_prompt_generation.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 6 errors during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
========================================================================== 6 errors in 0.15s ==========================================================================
((venv) ) Mac:jim backend[484]$ cd backend && pytest tests -q
bash: cd: backend: No such file or directory
((venv) ) Mac:jim backend[485]$ pwd
/Users/jim/Desktop/genai/sdd_connection_solver/backend
((venv) ) Mac:jim backend[486]$ pytest tests -q
========================================================================= test session starts =========================================================================
platform darwin -- Python 3.12.11, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/jim/Desktop/genai/sdd_connection_solver/backend
configfile: pyproject.toml
plugins: asyncio-1.1.0, mock-3.15.0, anyio-4.10.0, langsmith-0.4.27
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 197 items / 1 error                                                                                                                                         

=============================================================================== ERRORS ================================================================================
____________________________________________________ ERROR collecting tests/performance/test_api_response_times.py ____________________________________________________
ImportError while importing test module '/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_api_response_times.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/performance/test_api_response_times.py:18: in <module>
    from src.main import app
src/main.py:27: in <module>
    from .api.health import router as health_router
src/api/health.py:8: in <module>
    from ..storage.session_storage import InMemorySessionStorage
E   ImportError: cannot import name 'InMemorySessionStorage' from 'src.storage.session_storage' (/Users/jim/Desktop/genai/sdd_connection_solver/backend/src/storage/session_storage.py)
========================================================================== warnings summary ===========================================================================
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
  /Users/jim/Desktop/genai/sdd_connection_solver/venv/lib/python3.12/site-packages/pydantic/fields.py:1062: PydanticDeprecatedSince20: `min_items` is deprecated and will be removed, use `min_length` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn('`min_items` is deprecated and will be removed, use `min_length` instead', DeprecationWarning)

../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
  /Users/jim/Desktop/genai/sdd_connection_solver/venv/lib/python3.12/site-packages/pydantic/fields.py:1068: PydanticDeprecatedSince20: `max_items` is deprecated and will be removed, use `max_length` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn('`max_items` is deprecated and will be removed, use `max_length` instead', DeprecationWarning)

src/models/group.py:29
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/group.py:29: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("theme")

src/models/group.py:51
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/group.py:51: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("words")

src/models/group.py:78
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/group.py:78: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("difficulty")

../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
  /Users/jim/Desktop/genai/sdd_connection_solver/venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

src/models/one_away_group.py:25
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/one_away_group.py:25: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("words")

src/models/one_away_group.py:52
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/one_away_group.py:52: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("explanation")

../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
  /Users/jim/Desktop/genai/sdd_connection_solver/venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298: PydanticDeprecatedSince20: `json_encoders` is deprecated. See https://docs.pydantic.dev/2.11/concepts/serialization/#custom-serializers for alternatives. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(

src/models/ai_context.py:39
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/ai_context.py:39: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("remaining_words")

src/models/ai_context.py:66
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/ai_context.py:66: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("incorrect_groups")

src/models/ai_context.py:95
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/ai_context.py:95: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("llm_prompt_template")

src/models/puzzle.py:30
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/puzzle.py:30: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("words")

src/models/puzzle.py:62
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/puzzle.py:62: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("uploaded_filename")

src/models/recommendation.py:38
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:38: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("recommended_words")

src/models/recommendation.py:65
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:65: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("explanation")

src/models/recommendation.py:87
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:87: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("user_evaluation")

src/models/recommendation.py:108
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:108: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("evaluation_timestamp")

src/models/recommendation.py:132
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:132: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("processing_time_ms")

src/models/session.py:47
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:47: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("status")

src/models/session.py:65
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:65: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("solved_groups_count")

src/models/session.py:82
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:82: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("remaining_words")

src/models/session.py:119
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:119: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("incorrect_evaluation_count")

src/models/session.py:136
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:136: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("recommendation_history")

src/models/session.py:159
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:159: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("last_activity")

src/models/word.py:22
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/word.py:22: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("text")

src/models/word.py:49
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/word.py:49: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("position")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================================================================= short test summary info =======================================================================
ERROR tests/performance/test_api_response_times.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
==================================================================== 49 warnings, 1 error in 0.23s ====================================================================
((venv) ) Mac:jim backend[487]$ pytest tests -q
========================================================================= test session starts =========================================================================
platform darwin -- Python 3.12.11, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/jim/Desktop/genai/sdd_connection_solver/backend
configfile: pyproject.toml
plugins: asyncio-1.1.0, mock-3.15.0, anyio-4.10.0, langsmith-0.4.27
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 215 items                                                                                                                                                   

tests/contract/test_history.py FFF.FFFFF                                                                                                                        [  4%]
tests/contract/test_puzzles_get.py FFF.F.FFF                                                                                                                    [  8%]
tests/contract/test_puzzles_upload.py ......F...                                                                                                                [ 13%]
tests/contract/test_recommendations_create.py FF.....FFFF                                                                                                       [ 18%]
tests/contract/test_recommendations_evaluate.py FFF.F..FF..F                                                                                                    [ 23%]
tests/contract/test_recommendations_get.py F..F.......                                                                                                          [ 28%]
tests/contract/test_sessions_create.py FFF...FFFFF                                                                                                              [ 33%]
tests/contract/test_sessions_get.py FFFFFF.FFFFF                                                                                                                [ 39%]
tests/integration/test_ai_recommendations.py FF                                                                                                                 [ 40%]
tests/integration/test_complete_game.py F                                                                                                                       [ 40%]
tests/integration/test_evaluation_flow.py F                                                                                                                     [ 41%]
tests/integration/test_puzzle_upload_flow.py F..F.                                                                                                              [ 43%]
tests/integration/test_session_creation.py FFF                                                                                                                  [ 45%]
tests/performance/test_api_response_times.py ..EEEEE........EEE                                                                                                 [ 53%]
tests/performance/test_recommendation_timing.py FFFFFFF...F                                                                                                     [ 58%]
tests/performance/test_websocket_capacity.py ..........                                                                                                         [ 63%]
tests/unit/test_context_service.py .FFF.F.FF.FFF.F.F..FFF.F..FF                                                                                                 [ 76%]
tests/unit/test_evaluation_logic.py .FFF......F......FF.                                                                                                        [ 85%]
tests/unit/test_prompt_generation.py ..........FFFFFFFF.F...FFFF..FF                                                                                            [100%]

=============================================================================== ERRORS ================================================================================
______________________________________________ ERROR at setup of TestAPIResponseTimes.test_session_create_response_time _______________________________________________
tests/performance/test_api_response_times.py:77: in mock_session_service
    mock_session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
________________________________________________ ERROR at setup of TestAPIResponseTimes.test_session_get_response_time ________________________________________________
tests/performance/test_api_response_times.py:77: in mock_session_service
    mock_session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
________________________________________________ ERROR at setup of TestAPIResponseTimes.test_history_get_response_time ________________________________________________
tests/performance/test_api_response_times.py:77: in mock_session_service
    mock_session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
____________________________________________ ERROR at setup of TestAPIResponseTimes.test_recommendations_get_response_time ____________________________________________
tests/performance/test_api_response_times.py:77: in mock_session_service
    mock_session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
______________________________________________ ERROR at setup of TestAPIResponseTimes.test_multiple_concurrent_requests _______________________________________________
tests/performance/test_api_response_times.py:77: in mock_session_service
    mock_session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'test-session-123'... 'user_id': 'test-user'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_____________________________________________ ERROR at setup of TestEndpointSpecificTiming.test_path_parameter_processing _____________________________________________
file /Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_api_response_times.py, line 377
      def test_path_parameter_processing(self, client: TestClient):
E       fixture 'client' not found
>       available fixtures: _class_scoped_runner, _function_scoped_runner, _module_scoped_runner, _package_scoped_runner, _session_scoped_runner, anyio_backend, anyio_backend_name, anyio_backend_options, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, class_mocker, doctest_namespace, event_loop_policy, free_tcp_port, free_tcp_port_factory, free_udp_port, free_udp_port_factory, mocker, module_mocker, monkeypatch, package_mocker, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, session_mocker, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, unused_udp_port, unused_udp_port_factory
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_api_response_times.py:377
____________________________________________ ERROR at setup of TestEndpointSpecificTiming.test_query_parameter_processing _____________________________________________
file /Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_api_response_times.py, line 395
      def test_query_parameter_processing(self, client: TestClient):
E       fixture 'client' not found
>       available fixtures: _class_scoped_runner, _function_scoped_runner, _module_scoped_runner, _package_scoped_runner, _session_scoped_runner, anyio_backend, anyio_backend_name, anyio_backend_options, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, class_mocker, doctest_namespace, event_loop_policy, free_tcp_port, free_tcp_port_factory, free_udp_port, free_udp_port_factory, mocker, module_mocker, monkeypatch, package_mocker, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, session_mocker, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, unused_udp_port, unused_udp_port_factory
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_api_response_times.py:395
______________________________________________ ERROR at setup of TestEndpointSpecificTiming.test_json_payload_processing ______________________________________________
file /Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_api_response_times.py, line 404
      def test_json_payload_processing(self, client: TestClient):
E       fixture 'client' not found
>       available fixtures: _class_scoped_runner, _function_scoped_runner, _module_scoped_runner, _package_scoped_runner, _session_scoped_runner, anyio_backend, anyio_backend_name, anyio_backend_options, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, class_mocker, doctest_namespace, event_loop_policy, free_tcp_port, free_tcp_port_factory, free_udp_port, free_udp_port_factory, mocker, module_mocker, monkeypatch, package_mocker, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, session_mocker, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, unused_udp_port, unused_udp_port_factory
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/jim/Desktop/genai/sdd_connection_solver/backend/tests/performance/test_api_response_times.py:404
============================================================================== FAILURES ===============================================================================
_________________________________________________________ TestHistoryContract.test_get_recommendation_history _________________________________________________________
tests/contract/test_history.py:41: in test_get_recommendation_history
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
E   AssertionError: Expected 200, got 404
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/12345678-1234-5678-9abc-123456789012/history: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 12345678-1234-5678-9abc-123456789012 not found'}
______________________________________________________ TestHistoryContract.test_get_history_chronological_order _______________________________________________________
tests/contract/test_history.py:126: in test_get_history_chronological_order
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/87654321-4321-8765-4321-876543210987/history: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 87654321-4321-8765-4321-876543210987 not found'}
_________________________________________________________ TestHistoryContract.test_get_history_empty_session __________________________________________________________
tests/contract/test_history.py:149: in test_get_history_empty_session
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/11111111-2222-3333-4444-555555555555/history: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 11111111-2222-3333-4444-555555555555 not found'}
______________________________________________________ TestHistoryContract.test_get_history_invalid_session_uuid ______________________________________________________
tests/contract/test_history.py:194: in test_get_history_invalid_session_uuid
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
E   AssertionError: Expected 400, got 404
E   assert 404 == 400
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/not-a-valid-uuid/history: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID not-a-valid-uuid not found'}
______________________________________________________ TestHistoryContract.test_get_history_summary_calculations ______________________________________________________
tests/contract/test_history.py:209: in test_get_history_summary_calculations
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/history: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee not found'}
___________________________________________________ TestHistoryContract.test_get_history_recommendation_uniqueness ____________________________________________________
tests/contract/test_history.py:252: in test_get_history_recommendation_uniqueness
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/ffff1111-2222-3333-4444-555566667777/history: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID ffff1111-2222-3333-4444-555566667777 not found'}
_____________________________________________________ TestHistoryContract.test_get_history_llm_model_consistency ______________________________________________________
tests/contract/test_history.py:271: in test_get_history_llm_model_consistency
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/22222222-3333-4444-5555-666666666666/history: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 22222222-3333-4444-5555-666666666666 not found'}
___________________________________________________ TestHistoryContract.test_get_history_processing_time_validation ___________________________________________________
tests/contract/test_history.py:290: in test_get_history_processing_time_validation
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/33333333-4444-5555-6666-777777777777/history: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 33333333-4444-5555-6666-777777777777 not found'}
________________________________________________________ TestPuzzlesGetContract.test_get_existing_puzzle_by_id ________________________________________________________
tests/contract/test_puzzles_get.py:42: in test_get_existing_puzzle_by_id
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
E   AssertionError: Expected 200, got 404
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/puzzles/12345678-1234-5678-9abc-123456789012: 404 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 12345678-1234-5678-9abc-123456789012 not found'}
_________________________________________________________ TestPuzzlesGetContract.test_get_puzzle_with_user_id _________________________________________________________
tests/contract/test_puzzles_get.py:84: in test_get_puzzle_with_user_id
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/puzzles/87654321-4321-8765-4321-876543210987: 404 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 87654321-4321-8765-4321-876543210987 not found'}
______________________________________________________ TestPuzzlesGetContract.test_get_puzzle_anonymous_session _______________________________________________________
tests/contract/test_puzzles_get.py:102: in test_get_puzzle_anonymous_session
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/puzzles/11111111-2222-3333-4444-555555555555: 404 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 11111111-2222-3333-4444-555555555555 not found'}
_____________________________________________________ TestPuzzlesGetContract.test_get_puzzle_invalid_uuid_format ______________________________________________________
tests/contract/test_puzzles_get.py:141: in test_get_puzzle_invalid_uuid_format
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
E   AssertionError: Expected 400, got 404
E   assert 404 == 400
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/puzzles/not-a-valid-uuid: 404 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID not-a-valid-uuid not found'}
__________________________________________________ TestPuzzlesGetContract.test_get_puzzle_created_at_datetime_format __________________________________________________
tests/contract/test_puzzles_get.py:168: in test_get_puzzle_created_at_datetime_format
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/puzzles/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee: 404 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee not found'}
_____________________________________________________ TestPuzzlesGetContract.test_get_puzzle_filename_validation ______________________________________________________
tests/contract/test_puzzles_get.py:186: in test_get_puzzle_filename_validation
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/puzzles/ffff1111-2222-3333-4444-555566667777: 404 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID ffff1111-2222-3333-4444-555566667777 not found'}
______________________________________________________ TestPuzzlesGetContract.test_get_puzzle_words_constraints _______________________________________________________
tests/contract/test_puzzles_get.py:206: in test_get_puzzle_words_constraints
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/puzzles/12ab34cd-56ef-78gh-90ij-klmnopqrstuv: 404 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 12ab34cd-56ef-78gh-90ij-klmnopqrstuv not found'}
_______________________________________________________ TestPuzzlesUploadContract.test_upload_no_file_provided ________________________________________________________
tests/contract/test_puzzles_upload.py:166: in test_upload_no_file_provided
    assert response.status_code == 400
E   assert 422 == 400
E    +  where 422 = <Response [422 Unprocessable Entity]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:112 Validation error on http://testserver/api/v1/puzzles/upload: [{'type': 'missing', 'loc': ('body', 'file'), 'msg': 'Field required', 'input': None}]
__________________________________________ TestRecommendationsCreateContract.test_generate_recommendation_for_active_session __________________________________________
tests/contract/test_recommendations_create.py:41: in test_generate_recommendation_for_active_session
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
E   AssertionError: Expected 201, got 400
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/12345678-1234-5678-9abc-123456789012/recommendations: 400 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 12345678-1234-5678-9abc-123456789012 not found'}
___________________________________________ TestRecommendationsCreateContract.test_generate_recommendation_pending_conflict ___________________________________________
tests/contract/test_recommendations_create.py:88: in test_generate_recommendation_pending_conflict
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
E   AssertionError: Expected 409, got 400
E   assert 400 == 409
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/87654321-4321-8765-4321-876543210987/recommendations: 400 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 87654321-4321-8765-4321-876543210987 not found'}
_____________________________________________ TestRecommendationsCreateContract.test_generate_recommendation_unique_words _____________________________________________
tests/contract/test_recommendations_create.py:189: in test_generate_recommendation_unique_words
    assert response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/22222222-3333-4444-5555-666666666666/recommendations: 400 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 22222222-3333-4444-5555-666666666666 not found'}
_________________________________________ TestRecommendationsCreateContract.test_generate_recommendation_explanation_quality __________________________________________
tests/contract/test_recommendations_create.py:211: in test_generate_recommendation_explanation_quality
    assert response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/33333333-4444-5555-6666-777777777777/recommendations: 400 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 33333333-4444-5555-6666-777777777777 not found'}
___________________________________________ TestRecommendationsCreateContract.test_generate_recommendation_processing_time ____________________________________________
tests/contract/test_recommendations_create.py:232: in test_generate_recommendation_processing_time
    assert response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/44444444-5555-6666-7777-888888888888/recommendations: 400 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 44444444-5555-6666-7777-888888888888 not found'}
___________________________________________ TestRecommendationsCreateContract.test_generate_recommendation_timestamp_format ___________________________________________
tests/contract/test_recommendations_create.py:250: in test_generate_recommendation_timestamp_format
    assert response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/55555555-6666-7777-8888-999999999999/recommendations: 400 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 55555555-6666-7777-8888-999999999999 not found'}
______________________________________________ TestRecommendationsEvaluateContract.test_evaluate_recommendation_correct _______________________________________________
tests/contract/test_recommendations_evaluate.py:47: in test_evaluate_recommendation_correct
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
E   AssertionError: Expected 200, got 404
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/12345678-1234-5678-9abc-123456789012/recommendations/87654321-4321-8765-4321-876543210987/evaluate: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 12345678-1234-5678-9abc-123456789012 not found'}
_____________________________________________ TestRecommendationsEvaluateContract.test_evaluate_recommendation_incorrect ______________________________________________
tests/contract/test_recommendations_evaluate.py:106: in test_evaluate_recommendation_incorrect
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/11111111-2222-3333-4444-555555555555/recommendations/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/evaluate: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 11111111-2222-3333-4444-555555555555 not found'}
______________________________________________ TestRecommendationsEvaluateContract.test_evaluate_recommendation_one_away ______________________________________________
tests/contract/test_recommendations_evaluate.py:133: in test_evaluate_recommendation_one_away
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/22222222-3333-4444-5555-666666666666/recommendations/ffff1111-2222-3333-4444-555566667777/evaluate: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 22222222-3333-4444-5555-666666666666 not found'}
_________________________________________ TestRecommendationsEvaluateContract.test_evaluate_recommendation_missing_evaluation _________________________________________
tests/contract/test_recommendations_evaluate.py:185: in test_evaluate_recommendation_missing_evaluation
    assert response.status_code == 400
E   assert 422 == 400
E    +  where 422 = <Response [422 Unprocessable Entity]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:112 Validation error on http://testserver/api/v1/sessions/44444444-5555-6666-7777-888888888888/recommendations/55555555-6666-7777-8888-999999999999/evaluate: [{'type': 'missing', 'loc': ('body', 'evaluation'), 'msg': 'Field required', 'input': {}}]
_______________________________________________ TestRecommendationsEvaluateContract.test_evaluate_invalid_session_uuid ________________________________________________
tests/contract/test_recommendations_evaluate.py:249: in test_evaluate_invalid_session_uuid
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
E   AssertionError: Expected 400, got 404
E   assert 404 == 400
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/not-a-valid-uuid/recommendations/88888888-9999-aaaa-bbbb-cccccccccccc/evaluate: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID not-a-valid-uuid not found'}
____________________________________________ TestRecommendationsEvaluateContract.test_evaluate_invalid_recommendation_uuid ____________________________________________
tests/contract/test_recommendations_evaluate.py:270: in test_evaluate_invalid_recommendation_uuid
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
E   AssertionError: Expected 400, got 404
E   assert 404 == 400
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/99999999-aaaa-bbbb-cccc-dddddddddddd/recommendations/not-a-valid-uuid/evaluate: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 99999999-aaaa-bbbb-cccc-dddddddddddd not found'}
__________________________________________________ TestRecommendationsEvaluateContract.test_evaluate_malformed_json ___________________________________________________
tests/contract/test_recommendations_evaluate.py:344: in test_evaluate_malformed_json
    assert response.status_code == 400
E   assert 422 == 400
E    +  where 422 = <Response [422 Unprocessable Entity]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:112 Validation error on http://testserver/api/v1/sessions/eeeeeeee-ffff-gggg-hhhh-555555555555/recommendations/ffffffff-gggg-hhhh-iiii-666666666666/evaluate: [{'type': 'json_invalid', 'loc': ('body', 24), 'msg': 'JSON decode error', 'input': {}, 'ctx': {'error': "Expecting ',' delimiter"}}]
_______________________________________________ TestRecommendationsGetContract.test_get_current_pending_recommendation ________________________________________________
tests/contract/test_recommendations_get.py:41: in test_get_current_pending_recommendation
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
E   AssertionError: Expected 200, got 404
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/12345678-1234-5678-9abc-123456789012/recommendations: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 12345678-1234-5678-9abc-123456789012 not found'}
_____________________________________________ TestRecommendationsGetContract.test_get_recommendation_invalid_session_uuid _____________________________________________
tests/contract/test_recommendations_get.py:125: in test_get_recommendation_invalid_session_uuid
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
E   AssertionError: Expected 400, got 404
E   assert 404 == 400
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/not-a-valid-uuid/recommendations: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID not-a-valid-uuid not found'}
____________________________________________________ TestSessionsCreateContract.test_create_session_valid_request _____________________________________________________
tests/contract/test_sessions_create.py:47: in test_create_session_valid_request
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
E   AssertionError: Expected 201, got 400
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 12345678-1234-5678-9abc-123456789012 not found'}
___________________________________________________ TestSessionsCreateContract.test_create_session_without_user_id ____________________________________________________
tests/contract/test_sessions_create.py:105: in test_create_session_without_user_id
    assert response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 87654321-4321-8765-4321-876543210987 not found'}
____________________________________________________ TestSessionsCreateContract.test_create_session_all_llm_models ____________________________________________________
tests/contract/test_sessions_create.py:127: in test_create_session_all_llm_models
    assert response.status_code == 201, f"Failed for model: {model}"
E   AssertionError: Failed for model: gpt-4
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee not found'}
_______________________________________________ TestSessionsCreateContract.test_create_session_missing_required_fields ________________________________________________
tests/contract/test_sessions_create.py:188: in test_create_session_missing_required_fields
    assert response1.status_code == 400
E   assert 422 == 400
E    +  where 422 = <Response [422 Unprocessable Entity]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:112 Validation error on http://testserver/api/v1/sessions: [{'type': 'missing', 'loc': ('body', 'puzzle_id'), 'msg': 'Field required', 'input': {'llm_model': 'gpt-4'}}]
_________________________________________________ TestSessionsCreateContract.test_create_session_initial_state_values _________________________________________________
tests/contract/test_sessions_create.py:208: in test_create_session_initial_state_values
    assert response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 11111111-2222-3333-4444-555555555555 not found'}
___________________________________________________ TestSessionsCreateContract.test_create_session_datetime_format ____________________________________________________
tests/contract/test_sessions_create.py:233: in test_create_session_datetime_format
    assert response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 22222222-3333-4444-5555-666666666666 not found'}
____________________________________________________ TestSessionsCreateContract.test_create_session_malformed_json ____________________________________________________
tests/contract/test_sessions_create.py:261: in test_create_session_malformed_json
    assert response.status_code == 400
E   assert 422 == 400
E    +  where 422 = <Response [422 Unprocessable Entity]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:112 Validation error on http://testserver/api/v1/sessions: [{'type': 'json_invalid', 'loc': ('body', 28), 'msg': 'JSON decode error', 'input': {}, 'ctx': {'error': "Expecting ',' delimiter"}}]
______________________________________________ TestSessionsCreateContract.test_create_session_remaining_words_validation ______________________________________________
tests/contract/test_sessions_create.py:275: in test_create_session_remaining_words_validation
    assert response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 33333333-4444-5555-6666-777777777777 not found'}
_______________________________________________________ TestSessionsGetContract.test_get_existing_session_by_id _______________________________________________________
tests/contract/test_sessions_get.py:42: in test_get_existing_session_by_id
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
E   AssertionError: Expected 200, got 404
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/12345678-1234-5678-9abc-123456789012: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 12345678-1234-5678-9abc-123456789012 not found'}
_____________________________________________________ TestSessionsGetContract.test_get_session_with_solved_groups _____________________________________________________
tests/contract/test_sessions_get.py:104: in test_get_session_with_solved_groups
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/87654321-4321-8765-4321-876543210987: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 87654321-4321-8765-4321-876543210987 not found'}
________________________________________________ TestSessionsGetContract.test_get_session_with_pending_recommendation _________________________________________________
tests/contract/test_sessions_get.py:134: in test_get_session_with_pending_recommendation
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/11111111-2222-3333-4444-555555555555: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 11111111-2222-3333-4444-555555555555 not found'}
_______________________________________________________ TestSessionsGetContract.test_get_session_active_status ________________________________________________________
tests/contract/test_sessions_get.py:153: in test_get_session_active_status
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee not found'}
______________________________________________________ TestSessionsGetContract.test_get_session_completed_status ______________________________________________________
tests/contract/test_sessions_get.py:171: in test_get_session_completed_status
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/ffff1111-2222-3333-4444-555566667777: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID ffff1111-2222-3333-4444-555566667777 not found'}
_______________________________________________________ TestSessionsGetContract.test_get_session_failed_status ________________________________________________________
tests/contract/test_sessions_get.py:191: in test_get_session_failed_status
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/12ab34cd-56ef-78gh-90ij-klmnopqrstuv: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 12ab34cd-56ef-78gh-90ij-klmnopqrstuv not found'}
____________________________________________________ TestSessionsGetContract.test_get_session_invalid_uuid_format _____________________________________________________
tests/contract/test_sessions_get.py:232: in test_get_session_invalid_uuid_format
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
E   AssertionError: Expected 400, got 404
E   assert 404 == 400
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/not-a-valid-uuid: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID not-a-valid-uuid not found'}
__________________________________________________________ TestSessionsGetContract.test_get_session_empty_id __________________________________________________________
tests/contract/test_sessions_get.py:248: in test_get_session_empty_id
    assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}"
E   AssertionError: Expected 400 or 404, got 405
E   assert 405 in [400, 404]
E    +  where 405 = <Response [405 Method Not Allowed]>.status_code
________________________________________________ TestSessionsGetContract.test_get_session_remaining_words_constraints _________________________________________________
tests/contract/test_sessions_get.py:259: in test_get_session_remaining_words_constraints
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/22222222-3333-4444-5555-666666666666: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 22222222-3333-4444-5555-666666666666 not found'}
______________________________________________________ TestSessionsGetContract.test_get_session_datetime_format _______________________________________________________
tests/contract/test_sessions_get.py:284: in test_get_session_datetime_format
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/33333333-4444-5555-6666-777777777777: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 33333333-4444-5555-6666-777777777777 not found'}
_____________________________________________________ TestSessionsGetContract.test_get_session_state_consistency ______________________________________________________
tests/contract/test_sessions_get.py:312: in test_get_session_state_consistency
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions/44444444-5555-6666-7777-888888888888: 404 - {'error': 'SESSION_NOT_FOUND', 'message': 'Session with ID 44444444-5555-6666-7777-888888888888 not found'}
_______________________________________________ TestAIRecommendationsIntegration.test_complete_recommendation_workflow ________________________________________________
tests/integration/test_ai_recommendations.py:31: in test_complete_recommendation_workflow
    assert False, "AI recommendation integration not implemented"
E   AssertionError: AI recommendation integration not implemented
E   assert False
_________________________________________________ TestAIRecommendationsIntegration.test_context_aware_recommendations _________________________________________________
tests/integration/test_ai_recommendations.py:38: in test_context_aware_recommendations
    assert False, "Context-aware recommendation logic not implemented"
E   AssertionError: Context-aware recommendation logic not implemented
E   assert False
___________________________________________________ TestCompleteGameIntegration.test_complete_game_session_workflow ___________________________________________________
tests/integration/test_complete_game.py:27: in test_complete_game_session_workflow
    assert False, "Complete game workflow integration not implemented"
E   AssertionError: Complete game workflow integration not implemented
E   assert False
___________________________________________________ TestEvaluationFlowIntegration.test_complete_evaluation_workflow ___________________________________________________
tests/integration/test_evaluation_flow.py:27: in test_complete_evaluation_workflow
    assert False, "Evaluation workflow integration not implemented"
E   AssertionError: Evaluation workflow integration not implemented
E   assert False
________________________________________________ TestPuzzleUploadFlowIntegration.test_complete_puzzle_upload_workflow _________________________________________________
tests/integration/test_puzzle_upload_flow.py:65: in test_complete_puzzle_upload_workflow
    assert session_response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 133b803d-1295-4902-a1d1-fc920c793b4d not found'}
_______________________________________________ TestPuzzleUploadFlowIntegration.test_puzzle_upload_duplicate_detection ________________________________________________
tests/integration/test_puzzle_upload_flow.py:129: in test_puzzle_upload_duplicate_detection
    assert "duplicate" in error_data["message"].lower()
E   assert 'duplicate' in '{\'error\': \'validation_error\', \'message\': "1 validation error for puzzle\\nwords\\n  value error, all words must...\', \'word16\'], input_type=list]\\n    for further information visit https://errors.pydantic.dev/2.11/v/value_error"}'
E    +  where '{\'error\': \'validation_error\', \'message\': "1 validation error for puzzle\\nwords\\n  value error, all words must...\', \'word16\'], input_type=list]\\n    for further information visit https://errors.pydantic.dev/2.11/v/value_error"}' = <built-in method lower of str object at 0x1151ba4f0>()
E    +    where <built-in method lower of str object at 0x1151ba4f0> = '{\'error\': \'VALIDATION_ERROR\', \'message\': "1 validation error for Puzzle\\nwords\\n  Value error, All words must...\', \'WORD16\'], input_type=list]\\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error"}'.lower
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/puzzles/upload: 400 - {'error': 'VALIDATION_ERROR', 'message': "1 validation error for Puzzle\nwords\n  Value error, All words must be unique (case-insensitive) [type=value_error, input_value=['WORD1', 'WORD1', 'WORD3...14', 'WORD15', 'WORD16'], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error"}
_______________________________________________ TestSessionCreationIntegration.test_complete_session_creation_workflow ________________________________________________
tests/integration/test_session_creation.py:51: in test_complete_session_creation_workflow
    assert session_response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID 8747a00e-13f5-45a3-80b7-3695cc171132 not found'}
_____________________________________________ TestSessionCreationIntegration.test_session_remaining_words_initialization ______________________________________________
tests/integration/test_session_creation.py:105: in test_session_remaining_words_initialization
    assert session_response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID d5b60346-42ef-4721-adfc-2276ed5cebec not found'}
_______________________________________________ TestSessionCreationIntegration.test_session_multiple_users_same_puzzle ________________________________________________
tests/integration/test_session_creation.py:131: in test_session_multiple_users_same_puzzle
    assert session_response.status_code == 201
E   assert 400 == 201
E    +  where 400 = <Response [400 Bad Request]>.status_code
-------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------
WARNING  src.main:main.py:131 HTTP exception on http://testserver/api/v1/sessions: 400 - {'error': 'PUZZLE_NOT_FOUND', 'message': 'Puzzle with ID d88cdad4-7d09-4964-b6eb-673d71ea6c4e not found'}
_________________________________________________ TestRecommendationTiming.test_single_recommendation_under_2_seconds _________________________________________________
tests/performance/test_recommendation_timing.py:55: in test_single_recommendation_under_2_seconds
    recommendation = await llm_service.generate_recommendation(
src/services/llm_service.py:58: in generate_recommendation
    prompt = self._build_context_aware_prompt(context)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:112: in _build_context_aware_prompt
    context_info = self._format_context_information(context)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:145: in _format_context_information
    hint = f" (hint: {group.correct_connection})" if group.correct_connection else ""
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^
../venv/lib/python3.12/site-packages/pydantic/main.py:991: in __getattr__
    raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')
E   AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
_________________________________________________ TestRecommendationTiming.test_recommendation_engine_under_2_seconds _________________________________________________
tests/performance/test_recommendation_timing.py:78: in test_recommendation_engine_under_2_seconds
    recommendation = await recommendation_engine.generate_recommendation(
E   TypeError: RecommendationEngine.generate_recommendation() missing 1 required positional argument: 'ai_context'
________________________________________________________ TestRecommendationTiming.test_multiple_models_timing _________________________________________________________
tests/performance/test_recommendation_timing.py:100: in test_multiple_models_timing
    recommendation = await llm_service.generate_recommendation(
src/services/llm_service.py:58: in generate_recommendation
    prompt = self._build_context_aware_prompt(context)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:112: in _build_context_aware_prompt
    context_info = self._format_context_information(context)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:145: in _format_context_information
    hint = f" (hint: {group.correct_connection})" if group.correct_connection else ""
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^
../venv/lib/python3.12/site-packages/pydantic/main.py:991: in __getattr__
    raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')
E   AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
___________________________________________________ TestRecommendationTiming.test_concurrent_recommendations_timing ___________________________________________________
tests/performance/test_recommendation_timing.py:127: in test_concurrent_recommendations_timing
    elapsed_times = await asyncio.gather(*tasks)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/performance/test_recommendation_timing.py:120: in generate_single_recommendation
    await llm_service.generate_recommendation(session_id=session_id, context=sample_context, llm_model="gpt-4")
src/services/llm_service.py:58: in generate_recommendation
    prompt = self._build_context_aware_prompt(context)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:112: in _build_context_aware_prompt
    context_info = self._format_context_information(context)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:145: in _format_context_information
    hint = f" (hint: {group.correct_connection})" if group.correct_connection else ""
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^
../venv/lib/python3.12/site-packages/pydantic/main.py:991: in __getattr__
    raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')
E   AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
_________________________________________________________ TestRecommendationTiming.test_large_context_timing __________________________________________________________
tests/performance/test_recommendation_timing.py:160: in test_large_context_timing
    recommendation = await llm_service.generate_recommendation(
src/services/llm_service.py:58: in generate_recommendation
    prompt = self._build_context_aware_prompt(context)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:112: in _build_context_aware_prompt
    context_info = self._format_context_information(context)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:145: in _format_context_information
    hint = f" (hint: {group.correct_connection})" if group.correct_connection else ""
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^
../venv/lib/python3.12/site-packages/pydantic/main.py:991: in __getattr__
    raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')
E   AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
__________________________________________________________ TestRecommendationTiming.test_timing_consistency ___________________________________________________________
tests/performance/test_recommendation_timing.py:182: in test_timing_consistency
    await llm_service.generate_recommendation(
src/services/llm_service.py:58: in generate_recommendation
    prompt = self._build_context_aware_prompt(context)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:112: in _build_context_aware_prompt
    context_info = self._format_context_information(context)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:145: in _format_context_information
    hint = f" (hint: {group.correct_connection})" if group.correct_connection else ""
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^
../venv/lib/python3.12/site-packages/pydantic/main.py:991: in __getattr__
    raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')
E   AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
_______________________________________________________ TestRecommendationTiming.test_processing_time_tracking ________________________________________________________
tests/performance/test_recommendation_timing.py:204: in test_processing_time_tracking
    recommendation = await llm_service.generate_recommendation(
src/services/llm_service.py:58: in generate_recommendation
    prompt = self._build_context_aware_prompt(context)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:112: in _build_context_aware_prompt
    context_info = self._format_context_information(context)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/services/llm_service.py:145: in _format_context_information
    hint = f" (hint: {group.correct_connection})" if group.correct_connection else ""
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^
../venv/lib/python3.12/site-packages/pydantic/main.py:991: in __getattr__
    raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')
E   AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
________________________________________________________ TestPerformanceEdgeCases.test_maximum_context_timing _________________________________________________________
tests/performance/test_recommendation_timing.py:308: in test_maximum_context_timing
    OneAwayGroup(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for OneAwayGroup
E   words
E     Field required [type=missing, input_value={'attempted_words': ['one...ection': 'Connection 0'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   explanation
E     Field required [type=missing, input_value={'attempted_words': ['one...ection': 'Connection 0'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_________________________________________________________ TestContextService.test_create_context_for_session __________________________________________________________
tests/unit/test_context_service.py:25: in test_create_context_for_session
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
________________________________________________ TestContextService.test_create_context_for_session_with_custom_words _________________________________________________
tests/unit/test_context_service.py:47: in test_create_context_for_session_with_custom_words
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_______________________________________________________ TestContextService.test_get_context_for_session_exists ________________________________________________________
tests/unit/test_context_service.py:65: in test_get_context_for_session_exists
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
______________________________________________________ TestContextService.test_update_context_with_solved_group _______________________________________________________
tests/unit/test_context_service.py:86: in test_update_context_with_solved_group
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (8) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cher..., 'dog', 'bird', 'fish'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_____________________________________________________ TestContextService.test_update_context_with_incorrect_group _____________________________________________________
tests/unit/test_context_service.py:122: in test_update_context_with_incorrect_group
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
________________________________________________ TestContextService.test_update_context_with_incorrect_group_duplicate ________________________________________________
tests/unit/test_context_service.py:147: in test_update_context_with_incorrect_group_duplicate
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_____________________________________________________ TestContextService.test_update_context_with_one_away_group ______________________________________________________
tests/unit/test_context_service.py:176: in test_update_context_with_one_away_group
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_________________________________________________ TestContextService.test_update_context_with_one_away_group_minimal __________________________________________________
tests/unit/test_context_service.py:205: in test_update_context_with_one_away_group_minimal
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
________________________________________________ TestContextService.test_update_context_with_one_away_group_duplicate _________________________________________________
tests/unit/test_context_service.py:227: in test_update_context_with_one_away_group_duplicate
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
__________________________________________________________ TestContextService.test_generate_context_summary ___________________________________________________________
tests/unit/test_context_service.py:256: in test_generate_context_summary
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (8) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cher..., 'dog', 'bird', 'fish'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
___________________________________________________________ TestContextService.test_update_prompt_template ____________________________________________________________
tests/unit/test_context_service.py:301: in test_update_prompt_template
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
______________________________________________________ TestContextService.test_get_context_statistics_with_data _______________________________________________________
tests/unit/test_context_service.py:348: in test_get_context_statistics_with_data
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_0', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_________________________________________________________ TestContextService.test_cleanup_completed_contexts __________________________________________________________
tests/unit/test_context_service.py:382: in test_cleanup_completed_contexts
    active_session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'active_session', ...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
________________________________________________________________ TestContextService.test_reset_context ________________________________________________________________
tests/unit/test_context_service.py:426: in test_reset_context
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (8) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cher..., 'dog', 'bird', 'fish'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_______________________________________________________________ TestContextService.test_delete_context ________________________________________________________________
tests/unit/test_context_service.py:468: in test_delete_context
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
______________________________________________________________ TestContextService.test_context_isolation ______________________________________________________________
tests/unit/test_context_service.py:505: in test_context_isolation
    session1 = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (4) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cherry', 'date'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_________________________________________________________ TestContextService.test_update_preserves_other_data _________________________________________________________
tests/unit/test_context_service.py:534: in test_update_preserves_other_data
    session = Session(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
E   remaining_words
E     Value error, Remaining words count (8) doesn't match expected (16) based on solved groups (0) [type=value_error, input_value=['apple', 'banana', 'cher..., 'dog', 'bird', 'fish'], input_type=list]
E       For further information visit https://errors.pydantic.dev/2.11/v/value_error
E   llm_model_config
E     Field required [type=missing, input_value={'id': 'session_1', 'puzz...], 'llm_model': 'gpt-4'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_____________________________________________________ TestEvaluationService.test_evaluate_recommendation_correct ______________________________________________________
tests/unit/test_evaluation_logic.py:35: in test_evaluate_recommendation_correct
    context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
E   llm_prompt_template
E     Field required [type=missing, input_value={'session_id': 'session_1..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
____________________________________________________ TestEvaluationService.test_evaluate_recommendation_incorrect _____________________________________________________
tests/unit/test_evaluation_logic.py:70: in test_evaluate_recommendation_incorrect
    context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
E   llm_prompt_template
E     Field required [type=missing, input_value={'session_id': 'session_1..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_____________________________________________________ TestEvaluationService.test_evaluate_recommendation_one_away _____________________________________________________
tests/unit/test_evaluation_logic.py:101: in test_evaluate_recommendation_one_away
    context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
E   llm_prompt_template
E     Field required [type=missing, input_value={'session_id': 'session_1..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
__________________________________________________ TestEvaluationService.test_analyze_learning_patterns_improvement ___________________________________________________
tests/unit/test_evaluation_logic.py:248: in test_analyze_learning_patterns_improvement
    assert any("improvement" in insight for insight in patterns["insights"])
E   assert False
E    +  where False = any(<generator object TestEvaluationService.test_analyze_learning_patterns_improvement.<locals>.<genexpr> at 0x1155cc110>)
____________________________________________________ TestEvaluationService.test_context_update_preserves_original _____________________________________________________
tests/unit/test_evaluation_logic.py:395: in test_context_update_preserves_original
    original_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
E   llm_prompt_template
E     Field required [type=missing, input_value={'session_id': 'session_1..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
__________________________________________________ TestEvaluationService.test_evaluation_with_existing_solved_groups __________________________________________________
tests/unit/test_evaluation_logic.py:428: in test_evaluation_with_existing_solved_groups
    existing_group = Group(words=["red", "blue", "green", "yellow"], theme="Colors", difficulty_level=1, position=1)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for Group
E   difficulty
E     Field required [type=missing, input_value={'words': ['red', 'blue',...evel': 1, 'position': 1}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_______________________________________________________ TestPromptTemplateManager.test_generate_prompt_success ________________________________________________________
tests/unit/test_prompt_generation.py:171: in test_generate_prompt_success
    ai_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
__________________________________________________ TestPromptTemplateManager.test_generate_prompt_template_not_found __________________________________________________
tests/unit/test_prompt_generation.py:186: in test_generate_prompt_template_not_found
    ai_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_______________________________________________________ TestPromptTemplateManager.test_select_template_initial ________________________________________________________
tests/unit/test_prompt_generation.py:198: in test_select_template_initial
    ai_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
____________________________________________________ TestPromptTemplateManager.test_select_template_context_aware _____________________________________________________
tests/unit/test_prompt_generation.py:211: in test_select_template_context_aware
    ai_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
___________________________________________________ TestPromptTemplateManager.test_select_template_one_away_focused ___________________________________________________
tests/unit/test_prompt_generation.py:224: in test_select_template_one_away_focused
    one_away_group = OneAwayGroup(attempted_words=["apple", "banana", "cherry", "grape"], feedback="One away!")
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for OneAwayGroup
E   words
E     Field required [type=missing, input_value={'attempted_words': ['app...'feedback': 'One away!'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   explanation
E     Field required [type=missing, input_value={'attempted_words': ['app...'feedback': 'One away!'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
____________________________________________________ TestPromptTemplateManager.test_select_template_final_attempt _____________________________________________________
tests/unit/test_prompt_generation.py:238: in test_select_template_final_attempt
    ai_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
___________________________________________________ TestPromptTemplateManager.test_build_context_variables_minimal ____________________________________________________
tests/unit/test_prompt_generation.py:255: in test_build_context_variables_minimal
    ai_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_____________________________________________________ TestPromptTemplateManager.test_build_context_variables_full _____________________________________________________
tests/unit/test_prompt_generation.py:278: in test_build_context_variables_full
    solved_group = Group(words=["red", "blue", "green", "yellow"], theme="Colors", difficulty="easy")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for Group
E   difficulty
E     String should match pattern '^(yellow|green|blue|purple)$' [type=string_pattern_mismatch, input_value='easy', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.11/v/string_pattern_mismatch
____________________________________________________ TestPromptTemplateManager.test_format_solved_groups_multiple _____________________________________________________
tests/unit/test_prompt_generation.py:310: in test_format_solved_groups_multiple
    Group(words=["red", "blue", "green", "yellow"], theme="Colors", difficulty="easy"),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for Group
E   difficulty
E     String should match pattern '^(yellow|green|blue|purple)$' [type=string_pattern_mismatch, input_value='easy', input_type=str]
E       For further information visit https://errors.pydantic.dev/2.11/v/string_pattern_mismatch
__________________________________________________ TestPromptTemplateManager.test_format_one_away_attempts_multiple ___________________________________________________
tests/unit/test_prompt_generation.py:346: in test_format_one_away_attempts_multiple
    OneAwayGroup(attempted_words=["apple", "banana", "cherry", "grape"], feedback="One away!"),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for OneAwayGroup
E   words
E     Field required [type=missing, input_value={'attempted_words': ['app...'feedback': 'One away!'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   explanation
E     Field required [type=missing, input_value={'attempted_words': ['app...'feedback': 'One away!'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
____________________________________________________ TestPromptGeneration.test_get_prompt_for_context_auto_select _____________________________________________________
tests/unit/test_prompt_generation.py:361: in test_get_prompt_for_context_auto_select
    ai_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_________________________________________________ TestPromptGeneration.test_get_prompt_for_context_specific_template __________________________________________________
tests/unit/test_prompt_generation.py:376: in test_get_prompt_for_context_specific_template
    ai_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
___________________________________________________ TestPromptGeneration.test_get_prompt_for_context_extra_context ____________________________________________________
tests/unit/test_prompt_generation.py:391: in test_get_prompt_for_context_extra_context
    ai_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_______________________________________________________ TestPromptGeneration.test_template_variable_consistency _______________________________________________________
tests/unit/test_prompt_generation.py:456: in test_template_variable_consistency
    OneAwayGroup(attempted_words=["apple", "banana", "cherry", "grape"], feedback="One away!")
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for OneAwayGroup
E   words
E     Field required [type=missing, input_value={'attempted_words': ['app...'feedback': 'One away!'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   explanation
E     Field required [type=missing, input_value={'attempted_words': ['app...'feedback': 'One away!'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
_______________________________________________________ TestPromptGeneration.test_template_context_sensitivity ________________________________________________________
tests/unit/test_prompt_generation.py:474: in test_template_context_sensitivity
    initial_context = AIRecommendationContext(
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
E   session_id
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
E   llm_prompt_template
E     Field required [type=missing, input_value={'remaining_words': ['app..., 'one_away_groups': []}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.11/v/missing
========================================================================== warnings summary ===========================================================================
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
../venv/lib/python3.12/site-packages/pydantic/fields.py:1062
  /Users/jim/Desktop/genai/sdd_connection_solver/venv/lib/python3.12/site-packages/pydantic/fields.py:1062: PydanticDeprecatedSince20: `min_items` is deprecated and will be removed, use `min_length` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn('`min_items` is deprecated and will be removed, use `min_length` instead', DeprecationWarning)

../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
../venv/lib/python3.12/site-packages/pydantic/fields.py:1068
  /Users/jim/Desktop/genai/sdd_connection_solver/venv/lib/python3.12/site-packages/pydantic/fields.py:1068: PydanticDeprecatedSince20: `max_items` is deprecated and will be removed, use `max_length` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn('`max_items` is deprecated and will be removed, use `max_length` instead', DeprecationWarning)

src/models/group.py:29
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/group.py:29: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("theme")

src/models/group.py:51
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/group.py:51: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("words")

src/models/group.py:78
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/group.py:78: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("difficulty")

../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
../venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
  /Users/jim/Desktop/genai/sdd_connection_solver/venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

src/models/one_away_group.py:25
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/one_away_group.py:25: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("words")

src/models/one_away_group.py:52
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/one_away_group.py:52: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("explanation")

../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
../venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298
  /Users/jim/Desktop/genai/sdd_connection_solver/venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:298: PydanticDeprecatedSince20: `json_encoders` is deprecated. See https://docs.pydantic.dev/2.11/concepts/serialization/#custom-serializers for alternatives. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(

src/models/ai_context.py:39
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/ai_context.py:39: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("remaining_words")

src/models/ai_context.py:66
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/ai_context.py:66: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("incorrect_groups")

src/models/ai_context.py:95
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/ai_context.py:95: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("llm_prompt_template")

src/models/puzzle.py:30
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/puzzle.py:30: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("words")

src/models/puzzle.py:62
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/puzzle.py:62: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("uploaded_filename")

src/models/recommendation.py:38
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:38: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("recommended_words")

src/models/recommendation.py:65
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:65: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("explanation")

src/models/recommendation.py:87
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:87: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("user_evaluation")

src/models/recommendation.py:108
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:108: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("evaluation_timestamp")

src/models/recommendation.py:132
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/recommendation.py:132: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("processing_time_ms")

src/models/session.py:47
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:47: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("status")

src/models/session.py:65
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:65: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("solved_groups_count")

src/models/session.py:82
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:82: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("remaining_words")

src/models/session.py:119
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:119: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("incorrect_evaluation_count")

src/models/session.py:136
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:136: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("recommendation_history")

src/models/session.py:159
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/session.py:159: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("last_activity")

src/models/word.py:22
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/word.py:22: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("text")

src/models/word.py:49
  /Users/jim/Desktop/genai/sdd_connection_solver/backend/src/models/word.py:49: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator("position")

tests/contract/test_recommendations_evaluate.py::TestRecommendationsEvaluateContract::test_evaluate_malformed_json
tests/contract/test_sessions_create.py::TestSessionsCreateContract::test_create_session_malformed_json
  /Users/jim/Desktop/genai/sdd_connection_solver/venv/lib/python3.12/site-packages/httpx/_models.py:408: DeprecationWarning: Use 'content=<...>' to upload raw bytes/text content.
    headers, stream = encode_request(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================================================================= short test summary info =======================================================================
FAILED tests/contract/test_history.py::TestHistoryContract::test_get_recommendation_history - AssertionError: Expected 200, got 404
FAILED tests/contract/test_history.py::TestHistoryContract::test_get_history_chronological_order - assert 404 == 200
FAILED tests/contract/test_history.py::TestHistoryContract::test_get_history_empty_session - assert 404 == 200
FAILED tests/contract/test_history.py::TestHistoryContract::test_get_history_invalid_session_uuid - AssertionError: Expected 400, got 404
FAILED tests/contract/test_history.py::TestHistoryContract::test_get_history_summary_calculations - assert 404 == 200
FAILED tests/contract/test_history.py::TestHistoryContract::test_get_history_recommendation_uniqueness - assert 404 == 200
FAILED tests/contract/test_history.py::TestHistoryContract::test_get_history_llm_model_consistency - assert 404 == 200
FAILED tests/contract/test_history.py::TestHistoryContract::test_get_history_processing_time_validation - assert 404 == 200
FAILED tests/contract/test_puzzles_get.py::TestPuzzlesGetContract::test_get_existing_puzzle_by_id - AssertionError: Expected 200, got 404
FAILED tests/contract/test_puzzles_get.py::TestPuzzlesGetContract::test_get_puzzle_with_user_id - assert 404 == 200
FAILED tests/contract/test_puzzles_get.py::TestPuzzlesGetContract::test_get_puzzle_anonymous_session - assert 404 == 200
FAILED tests/contract/test_puzzles_get.py::TestPuzzlesGetContract::test_get_puzzle_invalid_uuid_format - AssertionError: Expected 400, got 404
FAILED tests/contract/test_puzzles_get.py::TestPuzzlesGetContract::test_get_puzzle_created_at_datetime_format - assert 404 == 200
FAILED tests/contract/test_puzzles_get.py::TestPuzzlesGetContract::test_get_puzzle_filename_validation - assert 404 == 200
FAILED tests/contract/test_puzzles_get.py::TestPuzzlesGetContract::test_get_puzzle_words_constraints - assert 404 == 200
FAILED tests/contract/test_puzzles_upload.py::TestPuzzlesUploadContract::test_upload_no_file_provided - assert 422 == 400
FAILED tests/contract/test_recommendations_create.py::TestRecommendationsCreateContract::test_generate_recommendation_for_active_session - AssertionError: Expected 201, got 400
FAILED tests/contract/test_recommendations_create.py::TestRecommendationsCreateContract::test_generate_recommendation_pending_conflict - AssertionError: Expected 409, got 400
FAILED tests/contract/test_recommendations_create.py::TestRecommendationsCreateContract::test_generate_recommendation_unique_words - assert 400 == 201
FAILED tests/contract/test_recommendations_create.py::TestRecommendationsCreateContract::test_generate_recommendation_explanation_quality - assert 400 == 201
FAILED tests/contract/test_recommendations_create.py::TestRecommendationsCreateContract::test_generate_recommendation_processing_time - assert 400 == 201
FAILED tests/contract/test_recommendations_create.py::TestRecommendationsCreateContract::test_generate_recommendation_timestamp_format - assert 400 == 201
FAILED tests/contract/test_recommendations_evaluate.py::TestRecommendationsEvaluateContract::test_evaluate_recommendation_correct - AssertionError: Expected 200, got 404
FAILED tests/contract/test_recommendations_evaluate.py::TestRecommendationsEvaluateContract::test_evaluate_recommendation_incorrect - assert 404 == 200
FAILED tests/contract/test_recommendations_evaluate.py::TestRecommendationsEvaluateContract::test_evaluate_recommendation_one_away - assert 404 == 200
FAILED tests/contract/test_recommendations_evaluate.py::TestRecommendationsEvaluateContract::test_evaluate_recommendation_missing_evaluation - assert 422 == 400
FAILED tests/contract/test_recommendations_evaluate.py::TestRecommendationsEvaluateContract::test_evaluate_invalid_session_uuid - AssertionError: Expected 400, got 404
FAILED tests/contract/test_recommendations_evaluate.py::TestRecommendationsEvaluateContract::test_evaluate_invalid_recommendation_uuid - AssertionError: Expected 400, got 404
FAILED tests/contract/test_recommendations_evaluate.py::TestRecommendationsEvaluateContract::test_evaluate_malformed_json - assert 422 == 400
FAILED tests/contract/test_recommendations_get.py::TestRecommendationsGetContract::test_get_current_pending_recommendation - AssertionError: Expected 200, got 404
FAILED tests/contract/test_recommendations_get.py::TestRecommendationsGetContract::test_get_recommendation_invalid_session_uuid - AssertionError: Expected 400, got 404
FAILED tests/contract/test_sessions_create.py::TestSessionsCreateContract::test_create_session_valid_request - AssertionError: Expected 201, got 400
FAILED tests/contract/test_sessions_create.py::TestSessionsCreateContract::test_create_session_without_user_id - assert 400 == 201
FAILED tests/contract/test_sessions_create.py::TestSessionsCreateContract::test_create_session_all_llm_models - AssertionError: Failed for model: gpt-4
FAILED tests/contract/test_sessions_create.py::TestSessionsCreateContract::test_create_session_missing_required_fields - assert 422 == 400
FAILED tests/contract/test_sessions_create.py::TestSessionsCreateContract::test_create_session_initial_state_values - assert 400 == 201
FAILED tests/contract/test_sessions_create.py::TestSessionsCreateContract::test_create_session_datetime_format - assert 400 == 201
FAILED tests/contract/test_sessions_create.py::TestSessionsCreateContract::test_create_session_malformed_json - assert 422 == 400
FAILED tests/contract/test_sessions_create.py::TestSessionsCreateContract::test_create_session_remaining_words_validation - assert 400 == 201
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_existing_session_by_id - AssertionError: Expected 200, got 404
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_with_solved_groups - assert 404 == 200
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_with_pending_recommendation - assert 404 == 200
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_active_status - assert 404 == 200
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_completed_status - assert 404 == 200
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_failed_status - assert 404 == 200
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_invalid_uuid_format - AssertionError: Expected 400, got 404
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_empty_id - AssertionError: Expected 400 or 404, got 405
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_remaining_words_constraints - assert 404 == 200
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_datetime_format - assert 404 == 200
FAILED tests/contract/test_sessions_get.py::TestSessionsGetContract::test_get_session_state_consistency - assert 404 == 200
FAILED tests/integration/test_ai_recommendations.py::TestAIRecommendationsIntegration::test_complete_recommendation_workflow - AssertionError: AI recommendation integration not implemented
FAILED tests/integration/test_ai_recommendations.py::TestAIRecommendationsIntegration::test_context_aware_recommendations - AssertionError: Context-aware recommendation logic not implemented
FAILED tests/integration/test_complete_game.py::TestCompleteGameIntegration::test_complete_game_session_workflow - AssertionError: Complete game workflow integration not implemented
FAILED tests/integration/test_evaluation_flow.py::TestEvaluationFlowIntegration::test_complete_evaluation_workflow - AssertionError: Evaluation workflow integration not implemented
FAILED tests/integration/test_puzzle_upload_flow.py::TestPuzzleUploadFlowIntegration::test_complete_puzzle_upload_workflow - assert 400 == 201
FAILED tests/integration/test_puzzle_upload_flow.py::TestPuzzleUploadFlowIntegration::test_puzzle_upload_duplicate_detection - assert 'duplicate' in '{\'error\': \'validation_error\', \'message\': "1 validation error for puzzle\\nwords\\n  value error, all words must...\', \'word16\'], in...
FAILED tests/integration/test_session_creation.py::TestSessionCreationIntegration::test_complete_session_creation_workflow - assert 400 == 201
FAILED tests/integration/test_session_creation.py::TestSessionCreationIntegration::test_session_remaining_words_initialization - assert 400 == 201
FAILED tests/integration/test_session_creation.py::TestSessionCreationIntegration::test_session_multiple_users_same_puzzle - assert 400 == 201
FAILED tests/performance/test_recommendation_timing.py::TestRecommendationTiming::test_single_recommendation_under_2_seconds - AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
FAILED tests/performance/test_recommendation_timing.py::TestRecommendationTiming::test_recommendation_engine_under_2_seconds - TypeError: RecommendationEngine.generate_recommendation() missing 1 required positional argument: 'ai_context'
FAILED tests/performance/test_recommendation_timing.py::TestRecommendationTiming::test_multiple_models_timing - AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
FAILED tests/performance/test_recommendation_timing.py::TestRecommendationTiming::test_concurrent_recommendations_timing - AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
FAILED tests/performance/test_recommendation_timing.py::TestRecommendationTiming::test_large_context_timing - AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
FAILED tests/performance/test_recommendation_timing.py::TestRecommendationTiming::test_timing_consistency - AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
FAILED tests/performance/test_recommendation_timing.py::TestRecommendationTiming::test_processing_time_tracking - AttributeError: 'OneAwayGroup' object has no attribute 'correct_connection'
FAILED tests/performance/test_recommendation_timing.py::TestPerformanceEdgeCases::test_maximum_context_timing - pydantic_core._pydantic_core.ValidationError: 2 validation errors for OneAwayGroup
FAILED tests/unit/test_context_service.py::TestContextService::test_create_context_for_session - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_create_context_for_session_with_custom_words - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_get_context_for_session_exists - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_update_context_with_solved_group - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_update_context_with_incorrect_group - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_update_context_with_incorrect_group_duplicate - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_update_context_with_one_away_group - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_update_context_with_one_away_group_minimal - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_update_context_with_one_away_group_duplicate - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_generate_context_summary - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_update_prompt_template - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_get_context_statistics_with_data - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_cleanup_completed_contexts - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_reset_context - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_delete_context - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_context_isolation - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_context_service.py::TestContextService::test_update_preserves_other_data - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
FAILED tests/unit/test_evaluation_logic.py::TestEvaluationService::test_evaluate_recommendation_correct - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_evaluation_logic.py::TestEvaluationService::test_evaluate_recommendation_incorrect - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_evaluation_logic.py::TestEvaluationService::test_evaluate_recommendation_one_away - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_evaluation_logic.py::TestEvaluationService::test_analyze_learning_patterns_improvement - assert False
FAILED tests/unit/test_evaluation_logic.py::TestEvaluationService::test_context_update_preserves_original - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_evaluation_logic.py::TestEvaluationService::test_evaluation_with_existing_solved_groups - pydantic_core._pydantic_core.ValidationError: 1 validation error for Group
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_generate_prompt_success - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_generate_prompt_template_not_found - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_select_template_initial - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_select_template_context_aware - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_select_template_one_away_focused - pydantic_core._pydantic_core.ValidationError: 2 validation errors for OneAwayGroup
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_select_template_final_attempt - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_build_context_variables_minimal - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_build_context_variables_full - pydantic_core._pydantic_core.ValidationError: 1 validation error for Group
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_format_solved_groups_multiple - pydantic_core._pydantic_core.ValidationError: 1 validation error for Group
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_format_one_away_attempts_multiple - pydantic_core._pydantic_core.ValidationError: 2 validation errors for OneAwayGroup
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_get_prompt_for_context_auto_select - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_get_prompt_for_context_specific_template - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_get_prompt_for_context_extra_context - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_template_variable_consistency - pydantic_core._pydantic_core.ValidationError: 2 validation errors for OneAwayGroup
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_template_context_sensitivity - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
ERROR tests/performance/test_api_response_times.py::TestAPIResponseTimes::test_session_create_response_time - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
ERROR tests/performance/test_api_response_times.py::TestAPIResponseTimes::test_session_get_response_time - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
ERROR tests/performance/test_api_response_times.py::TestAPIResponseTimes::test_history_get_response_time - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
ERROR tests/performance/test_api_response_times.py::TestAPIResponseTimes::test_recommendations_get_response_time - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
ERROR tests/performance/test_api_response_times.py::TestAPIResponseTimes::test_multiple_concurrent_requests - pydantic_core._pydantic_core.ValidationError: 2 validation errors for Session
ERROR tests/performance/test_api_response_times.py::TestEndpointSpecificTiming::test_path_parameter_processing
ERROR tests/performance/test_api_response_times.py::TestEndpointSpecificTiming::test_query_parameter_processing
ERROR tests/performance/test_api_response_times.py::TestEndpointSpecificTiming::test_json_payload_processing
======================================================= 105 failed, 102 passed, 51 warnings, 8 errors in 6.08s ========================================================
((venv) ) Mac:jim backend[488]$ 
```