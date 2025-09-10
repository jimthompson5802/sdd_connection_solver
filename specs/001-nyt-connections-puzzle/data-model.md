# Data Model: NYT Connections Puzzle Assistant

**Date**: September 8, 2025  
**Feature**: 001-nyt-connections-puzzle  

## Core Entities

### Puzzle
**Purpose**: Represents a complete NYT Connections puzzle instance created from user file upload
**Fields**:
- `id: str` - Unique puzzle identifier (UUID)
- `words: List[str]` - Exactly 16 user-uploaded words (from CSV file)
- `uploaded_filename: str` - Original filename of uploaded text file
- `created_at: datetime` - Puzzle creation timestamp
- `user_id: str | None` - User identifier (None for anonymous sessions)

**Validation Rules**:
- Must have exactly 16 words from uploaded CSV file
- All words must be unique (case-insensitive)
- Words must be non-empty strings, max 20 characters each
- `uploaded_filename` must be valid filename with .txt or .csv extension

**State Transitions**: 
- Uploaded → Active (when first recommendation requested)
- Active → Completed (when all groups found)
- Active → Failed (when 4 incorrect evaluations made)

### Word
**Purpose**: Individual puzzle element from uploaded file
**Fields**:
- `text: str` - The word text as uploaded (e.g., "BASS", "PIANO")
- `position: int` - Position in uploaded file (0-15)
- `is_solved: bool` - Whether this word is part of a correctly identified group

**Validation Rules**:
- `text` must be non-empty, alphanumeric plus common punctuation
- `text` length must be <= 20 characters
- `position` must be unique within puzzle (0-15)
- `is_solved` defaults to false

### Group
**Purpose**: A set of 4 related words with common theme/connection (hidden solution)
**Fields**:
- `id: str` - Unique group identifier
- `theme: str` - The connection description (e.g., "Types of Fish", "Musical Instruments")
- `words: List[str]` - Exactly 4 words in this group (word texts)
- `is_solved: bool` - Whether user has correctly identified this group
- `difficulty: str` - Group difficulty level ("yellow", "green", "blue", "purple")

**Validation Rules**:
- Must have exactly 4 words
- `theme` must be descriptive (3-50 characters)
- `difficulty` must be one of the 4 standard NYT levels
- All words must exist in the puzzle's word list

**State Transitions**:
- Hidden → Solved (when user correctly evaluates matching recommendation)

### Recommendation
**Purpose**: Records an AI-generated group suggestion and user's evaluation
**Fields**:
- `id: str` - Unique recommendation identifier
- `session_id: str` - Reference to user session
- `recommended_words: List[str]` - The 4 words AI recommended to group together
- `explanation: str` - AI's reasoning for this grouping
- `timestamp: datetime` - When recommendation was generated
- `user_evaluation: str | None` - User's response ("correct", "incorrect", "one_away", None if pending)
- `evaluation_timestamp: datetime | None` - When user evaluated the recommendation
- `llm_model: str` - Which LLM model generated this (configuration parameter)
- `processing_time_ms: int` - Time taken to generate recommendation

**Validation Rules**:
- Must have exactly 4 recommended words
- `recommended_words` must all exist in current puzzle's remaining words
- `explanation` must be 10-500 characters
- `user_evaluation` must be one of the 3 valid outcomes or None
- If `user_evaluation` is not None, `evaluation_timestamp` must be provided

**State Transitions**:
- Generated → Pending Evaluation → Evaluated (immutable after evaluation)

### Session
**Purpose**: Tracks user's current puzzle-solving session and progress
**Fields**:
- `id: str` - Unique session identifier
- `puzzle_id: str` - Reference to active puzzle
- `start_time: datetime` - Session start timestamp
- `last_activity: datetime` - Most recent user action
- `status: str` - Current session state ("active", "completed", "failed", "abandoned")
- `solved_groups_count: int` - Number of groups correctly identified (0-4)
- `remaining_words: List[str]` - Words still available for recommendations
- `incorrect_evaluation_count: int` - Number of incorrect evaluations made (max 4)
- `recommendation_history: List[Recommendation]` - All recommendations made in this session
- `llm_model_config: str` - Configured LLM model for this session

**Validation Rules**:
- `incorrect_evaluation_count` must be 0-4
- `solved_groups_count` must be 0-4
- `remaining_words` count must equal 16 - (solved_groups_count * 4)
- `recommendation_history` must be chronologically ordered

**State Transitions**:
- Created → Active (first recommendation generated)
- Active → Completed (all 4 groups solved)
- Active → Failed (4 incorrect evaluations reached)
- Active → Abandoned (timeout or explicit abandonment)

### AIRecommendationContext
**Purpose**: Stores context information used by LLM to generate recommendations
**Fields**:
- `id: str` - Unique context identifier
- `session_id: str` - Reference to session this context belongs to
- `remaining_words: List[str]` - Available words at time of recommendation
- `incorrect_groups: List[List[str]]` - Previously incorrect word combinations
- `one_away_groups: List[OneAwayGroup]` - Groups marked as one-away with partial connection info
- `solved_groups: List[Group]` - Successfully identified groups (for reference)
- `llm_prompt_template: str` - Template used for LLM prompting
- `created_at: datetime` - Context creation timestamp

**Validation Rules**:
- `remaining_words` must contain 4-16 words (depending on game progress)
- `incorrect_groups` must contain valid 4-word combinations from original puzzle
- Sum of words in all groups must not exceed 16

### OneAwayGroup  
**Purpose**: Stores information about a group marked as one-away (3/4 words correct, but unknown which)
**Fields**:
- `words: List[str]` - The 4 words from the one-away recommendation
- `explanation: str` - Original explanation for why these words were grouped
- `marked_at: datetime` - When this was marked as one-away

**Validation Rules**:
- Must have exactly 4 words
- `explanation` must be 10-500 characters  
- All words must exist in original puzzle
- System knows 3 out of 4 words belong together, but not which specific ones

## Entity Relationships

```
Puzzle (1) ←→ (1-*) Session
Session (1) ←→ (0-*) Recommendation  
Session (1) ←→ (0-*) AIRecommendationContext
Recommendation (0-1) ←→ (1) AIRecommendationContext
Session (1) ←→ (0-4) Group [solved groups]
AIRecommendationContext (1) ←→ (0-*) OneAwayGroup
```

## State Management

### Puzzle Lifecycle
1. **Uploaded**: User uploads 16-word CSV file, puzzle created
2. **Active**: First recommendation requested, session started  
3. **Completed**: All 4 groups correctly identified via recommendations
4. **Failed**: 4 incorrect evaluations exhausted

### Session State Flow
1. **Initialize**: Create session with uploaded puzzle (16 words available)
2. **Recommendation Loop**: Generate AI recommendation → User evaluates → Update state
3. **Correct Evaluation**: Remove 4 words from available, increment solved count
4. **Incorrect/One-Away Evaluation**: Increment incorrect count, track bad recommendation
5. **Terminal States**: Completed (4 groups solved) or Failed (4 incorrect evaluations)

### Data Consistency Rules
- `Session.remaining_words` = Original 16 words - words in solved groups
- `Session.incorrect_evaluation_count` = count of "incorrect" + "one_away" evaluations
- `Session.solved_groups_count` = number of correctly evaluated recommendations
- `AIRecommendationContext.remaining_words` must match `Session.remaining_words`
- Only one pending (unevaluated) `Recommendation` per session at a time

## Serialization Schemas

All entities serialize to JSON for API transport. Field names use snake_case in Python models and camelCase in TypeScript interfaces.

### API Response DTOs
- Entities may be serialized differently for API responses (e.g., hide `Group.theme` until solved)
- Puzzle responses exclude solution information during active gameplay
- Session responses include computed fields like `can_make_guess: bool`
