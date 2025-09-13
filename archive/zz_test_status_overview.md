
## Frontend Test Status Overivew

```shell
((venv) ) Mac:jim backend[501]$ cd ../frontend
((venv) ) Mac:jim frontend[502]$ npm test

> nyt-connections-puzzle-assistant@1.0.0 test
> jest

 PASS  tests/unit/fileupload.spec.ts
 PASS  tests/unit/recommendationcard.spec.ts
 PASS  tests/unit/gamestate.spec.ts
 PASS  tests/unit/evaluationbuttons.spec.ts
 PASS  tests/unit/puzzleview.spec.ts

Test Suites: 5 passed, 5 total
Tests:       5 passed, 5 total
Snapshots:   0 total
Time:        2.775 s
Ran all test suites.
```

## Playwright Test Status Overview
![](./images/playwright_test_status.png)

```shell

> nyt-connections-puzzle-assistant@1.0.0 test:e2e
> playwright test


Running 15 tests using 8 workers

      1 [chromium] › tests/e2e/test_evaluation.spec.ts:11:7 › Recommendation Evaluation Workflow › complete evaluation workflow
      2 [firefox] › tests/e2e/test_evaluation.spec.ts:26:7 › Recommendation Evaluation Workflow › evaluation state management
      3 [chromium] › tests/e2e/test_evaluation.spec.ts:26:7 › Recommendation Evaluation Workflow › evaluation state management
      4 [firefox] › tests/e2e/diagnostic_console.spec.ts:3:5 › diagnostic: capture browser console and errors
      5 [firefox] › tests/e2e/test_evaluation.spec.ts:11:7 › Recommendation Evaluation Workflow › complete evaluation workflow
      6 [chromium] › tests/e2e/test_file_upload.spec.ts:11:7 › File Upload and Puzzle Creation › complete file upload workflow
      7 [chromium] › tests/e2e/test_file_upload.spec.ts:26:7 › File Upload and Puzzle Creation › file validation and error handling
      8 [chromium] › tests/e2e/diagnostic_console.spec.ts:3:5 › diagnostic: capture browser console and errors
Starting diagnostic run: attaching listeners
[response 404] http://localhost:8080/styles.css
[browser console] error Failed to load resource: the server responded with a status of 404 (File not found) http://localhost:8080/styles.css:
[request failed] GET http://localhost:8080/styles.css - net::ERR_ABORTED
[response 404] http://localhost:8080/main.js
[browser console] error Failed to load resource: the server responded with a status of 404 (File not found) http://localhost:8080/main.js:
[request failed] GET http://localhost:8080/main.js - net::ERR_ABORTED
[browser console] log DOM content loaded - initializing app... http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log NYT Connections Puzzle Assistant - Starting Full Application... http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log [App] Initializing NYT Connections Puzzle Assistant... http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log [App] Initializing UI components... http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log [App] Application initialized successfully http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log Application initialized successfully with all components http://localhost:8080/main.d289db733fc9149d33f5.js:
Navigated to /, waiting 20s to capture console output...
Starting diagnostic run: attaching listeners
[response 404] http://localhost:8080/styles.css
[response 404] http://localhost:8080/main.js
[request failed] GET http://localhost:8080/main.js - NS_ERROR_CORRUPTED_CONTENT
[browser console] error [JavaScript Error: "Loading module from “http://localhost:8080/main.js” was blocked because of a disallowed MIME type (“text/html”)." {file: "http://localhost:8080/" line: 0}] http://localhost:8080/:
[browser console] warning [JavaScript Warning: "Loading failed for the module with source “http://localhost:8080/main.js”." {file: "http://localhost:8080/" line: 1}] http://localhost:8080/:1
[browser console] log DOM content loaded - initializing app... http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log NYT Connections Puzzle Assistant - Starting Full Application... http://localhost:8080/main.d289db733fc9149d33f5.js:
  ✘  13 [webkit] › tests/e2e/test_evaluation.spec.ts:26:7 › Recommendation Evaluation Workflow › evaluation state management (15.3s)
[browser console] log [App] Initializing UI components... http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log [App] Application initialized successfully http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log Application initialized successfully with all components http://localhost:8080/main.d289db733fc9149d33f5.js:
Navigated to /, waiting 20s to capture console output...
  ✘   3 [chromium] › tests/e2e/test_evaluation.spec.ts:26:7 › Recommendation Evaluation Workflow › evaluation state management (15.2s)
  ✘   7 [chromium] › tests/e2e/test_file_upload.spec.ts:26:7 › File Upload and Puzzle Creation › file validation and error handling (15.2s)
  ✘  14 [webkit] › tests/e2e/test_file_upload.spec.ts:11:7 › File Upload and Puzzle Creation › complete file upload workflow (15.2s)
  ✘   6 [chromium] › tests/e2e/test_file_upload.spec.ts:11:7 › File Upload and Puzzle Creation › complete file upload workflow (15.2s)
      9 [webkit] › tests/e2e/test_evaluation.spec.ts:11:7 › Recommendation Evaluation Workflow › complete evaluation workflow
     10 [firefox] › tests/e2e/test_file_upload.spec.ts:11:7 › File Upload and Puzzle Creation › complete file upload workflow
     11 [firefox] › tests/e2e/test_file_upload.spec.ts:26:7 › File Upload and Puzzle Creation › file validation and error handling
     12 [webkit] › tests/e2e/diagnostic_console.spec.ts:3:5 › diagnostic: capture browser console and errors
  ✘   5 [firefox] › tests/e2e/test_evaluation.spec.ts:11:7 › Recommendation Evaluation Workflow › complete evaluation workflow (15.5s)
Starting diagnostic run: attaching listeners
[response 404] http://localhost:8080/styles.css
[browser console] error Failed to load resource: the server responded with a status of 404 (File not found) http://localhost:8080/styles.css:
[request failed] GET http://localhost:8080/styles.css - cancelled
[response 404] http://localhost:8080/main.js
[browser console] error Failed to load resource: the server responded with a status of 404 (File not found) http://localhost:8080/main.js:
[request failed] GET http://localhost:8080/main.js - cancelled
[browser console] log DOM content loaded - initializing app... http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log NYT Connections Puzzle Assistant - Starting Full Application... http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log [App] Initializing NYT Connections Puzzle Assistant... http://localhost:8080/main.d289db733fc9149d33f5.js:
[browser console] log [App] Initializing UI components... http://localhost:8080/main.d289db733fc9149d33f5.js:
Navigated to /, waiting 20s to capture console output...
[browser console] log [App] Application initialized successfully http://localhost:8080/main.d289db733fc9149d33f5.js:
  ✘  15 [webkit] › tests/e2e/test_file_upload.spec.ts:26:7 › File Upload and Puzzle Creation › file validation and error handling (15.2s)
  ✘   2 [firefox] › tests/e2e/test_evaluation.spec.ts:26:7 › Recommendation Evaluation Workflow › evaluation state management (15.5s)
     13 [webkit] › tests/e2e/test_evaluation.spec.ts:26:7 › Recommendation Evaluation Workflow › evaluation state management
     14 [webkit] › tests/e2e/test_file_upload.spec.ts:11:7 › File Upload and Puzzle Creation › complete file upload workflow
Diagnostic run complete
  ✓   8 [chromium] › tests/e2e/diagnostic_console.spec.ts:3:5 › diagnostic: capture browser console and errors (20.1s)
     15 [webkit] › tests/e2e/test_file_upload.spec.ts:26:7 › File Upload and Puzzle Creation › file validation and error handling
Diagnostic run complete
  ✓   4 [firefox] › tests/e2e/diagnostic_console.spec.ts:3:5 › diagnostic: capture browser console and errors (20.5s)
  ✘   9 [webkit] › tests/e2e/test_evaluation.spec.ts:11:7 › Recommendation Evaluation Workflow › complete evaluation workflow (15.4s)
  ✘  10 [firefox] › tests/e2e/test_file_upload.spec.ts:11:7 › File Upload and Puzzle Creation › complete file upload workflow (15.5s)
  ✘  11 [firefox] › tests/e2e/test_file_upload.spec.ts:26:7 › File Upload and Puzzle Creation › file validation and error handling (15.5s)
Diagnostic run complete
  ✓  12 [webkit] › tests/e2e/diagnostic_console.spec.ts:3:5 › diagnostic: capture browser console and errors (20.4s)

  12 failed
    [chromium] › tests/e2e/test_evaluation.spec.ts:11:7 › Recommendation Evaluation Workflow › complete evaluation workflow 
    [chromium] › tests/e2e/test_evaluation.spec.ts:26:7 › Recommendation Evaluation Workflow › evaluation state management 
    [chromium] › tests/e2e/test_file_upload.spec.ts:11:7 › File Upload and Puzzle Creation › complete file upload workflow 
    [chromium] › tests/e2e/test_file_upload.spec.ts:26:7 › File Upload and Puzzle Creation › file validation and error handling 
    [firefox] › tests/e2e/test_evaluation.spec.ts:11:7 › Recommendation Evaluation Workflow › complete evaluation workflow 
    [firefox] › tests/e2e/test_evaluation.spec.ts:26:7 › Recommendation Evaluation Workflow › evaluation state management 
    [firefox] › tests/e2e/test_file_upload.spec.ts:11:7 › File Upload and Puzzle Creation › complete file upload workflow 
    [firefox] › tests/e2e/test_file_upload.spec.ts:26:7 › File Upload and Puzzle Creation › file validation and error handling 
    [webkit] › tests/e2e/test_evaluation.spec.ts:11:7 › Recommendation Evaluation Workflow › complete evaluation workflow 
    [webkit] › tests/e2e/test_evaluation.spec.ts:26:7 › Recommendation Evaluation Workflow › evaluation state management 
    [webkit] › tests/e2e/test_file_upload.spec.ts:11:7 › File Upload and Puzzle Creation › complete file upload workflow 
    [webkit] › tests/e2e/test_file_upload.spec.ts:26:7 › File Upload and Puzzle Creation › file validation and error handling 
  3 passed (41.4s)
```

## Backend Test Status Overview
```shell
((venv) ) Mac:jim backend[498]$ clear
((venv) ) Mac:jim backend[499]$ python -m pytest tests -q
================================================================== test session starts ==================================================================
platform darwin -- Python 3.12.11, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/jim/Desktop/genai/sdd_connection_solver/backend
configfile: pyproject.toml
plugins: asyncio-1.1.0, mock-3.15.0, anyio-4.10.0, langsmith-0.4.27
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 215 items                                                                                                                                     

tests/contract/test_history.py FFF.FFFFF                                                                                                          [  4%]
tests/contract/test_puzzles_get.py FFF.F.FFF                                                                                                      [  8%]
tests/contract/test_puzzles_upload.py ......F...                                                                                                  [ 13%]
tests/contract/test_recommendations_create.py FF.....FFFF                                                                                         [ 18%]
tests/contract/test_recommendations_evaluate.py FFF.F..FF..F                                                                                      [ 23%]
tests/contract/test_recommendations_get.py F..F.......                                                                                            [ 28%]
tests/contract/test_sessions_create.py FFF...FFFFF                                                                                                [ 33%]
tests/contract/test_sessions_get.py FFFFFF.FFFFF                                                                                                  [ 39%]
tests/integration/test_ai_recommendations.py FF                                                                                                   [ 40%]
tests/integration/test_complete_game.py F                                                                                                         [ 40%]
tests/integration/test_evaluation_flow.py F                                                                                                       [ 41%]
tests/integration/test_puzzle_upload_flow.py F..F.                                                                                                [ 43%]
tests/integration/test_session_creation.py FFF                                                                                                    [ 45%]
tests/performance/test_api_response_times.py ..F.FF.........EEE                                                                                   [ 53%]
tests/performance/test_recommendation_timing.py ..........F                                                                                       [ 58%]
tests/performance/test_websocket_capacity.py ..........                                                                                           [ 63%]
tests/unit/test_context_service.py ............................                                                                                   [ 76%]
tests/unit/test_evaluation_logic.py ...F......F.......F.                                                                                          [ 85%]
tests/unit/test_prompt_generation.py ..........FFFFFFFF.F...FFFF..FF                                                                              [100%]
================================================================ short test summary info ================================================================
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
FAILED tests/integration/test_puzzle_upload_flow.py::TestPuzzleUploadFlowIntegration::test_puzzle_upload_duplicate_detection - assert 'duplicate' in '{\'error\': \'validation_error\', \'message\': "1 validation error for puzzle\\nwords\\n  value error, all words must...\', \...
FAILED tests/integration/test_session_creation.py::TestSessionCreationIntegration::test_complete_session_creation_workflow - assert 400 == 201
FAILED tests/integration/test_session_creation.py::TestSessionCreationIntegration::test_session_remaining_words_initialization - assert 400 == 201
FAILED tests/integration/test_session_creation.py::TestSessionCreationIntegration::test_session_multiple_users_same_puzzle - assert 400 == 201
FAILED tests/performance/test_api_response_times.py::TestAPIResponseTimes::test_session_create_response_time - assert 400 == 201
FAILED tests/performance/test_api_response_times.py::TestAPIResponseTimes::test_history_get_response_time - pydantic_core._pydantic_core.ValidationError: 1 validation error for Session
FAILED tests/performance/test_api_response_times.py::TestAPIResponseTimes::test_recommendations_get_response_time - pydantic_core._pydantic_core.ValidationError: 1 validation error for Session
FAILED tests/performance/test_recommendation_timing.py::TestPerformanceEdgeCases::test_maximum_context_timing - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_evaluation_logic.py::TestEvaluationService::test_evaluate_recommendation_one_away - pydantic_core._pydantic_core.ValidationError: 2 validation errors for OneAwayGroup
FAILED tests/unit/test_evaluation_logic.py::TestEvaluationService::test_analyze_learning_patterns_improvement - assert False
FAILED tests/unit/test_evaluation_logic.py::TestEvaluationService::test_evaluation_with_existing_solved_groups - AttributeError: 'Group' object has no attribute 'position'
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_generate_prompt_success - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_generate_prompt_template_not_found - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_select_template_initial - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_select_template_context_aware - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_select_template_one_away_focused - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_select_template_final_attempt - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_build_context_variables_minimal - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_build_context_variables_full - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_format_solved_groups_multiple - pydantic_core._pydantic_core.ValidationError: 1 validation error for Group
FAILED tests/unit/test_prompt_generation.py::TestPromptTemplateManager::test_format_one_away_attempts_multiple - AttributeError: 'OneAwayGroup' object has no attribute 'attempted_words'
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_get_prompt_for_context_auto_select - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_get_prompt_for_context_specific_template - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_get_prompt_for_context_extra_context - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_template_variable_consistency - pydantic_core._pydantic_core.ValidationError: 2 validation errors for AIRecommendationContext
FAILED tests/unit/test_prompt_generation.py::TestPromptGeneration::test_template_context_sensitivity - pydantic_core._pydantic_core.ValidationError: 1 validation error for AIRecommendationContext
ERROR tests/performance/test_api_response_times.py::TestMemoryEfficiency::test_path_parameter_processing
ERROR tests/performance/test_api_response_times.py::TestMemoryEfficiency::test_query_parameter_processing
ERROR tests/performance/test_api_response_times.py::TestMemoryEfficiency::test_json_payload_processing
================================================= 81 failed, 131 passed, 49 warnings, 3 errors in 7.77s =================================================
((venv) ) Mac:jim backend[500]$ 
```

