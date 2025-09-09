# Data Model: NYT Connections Puzzle Assistant

**Date**: September 8, 2025  
**Feature**: 001-nyt-connections-puzzle  

## Core Entities

### Puzzle
**Purpose**: Represents a complete NYT Connections puzzle instance
**Fields**:
- `id: str` - Unique puzzle identifier (UUID)
- `words: List[Word]` - Exactly 16 puzzle words
- `groups: List[Group]` - The 4 correct groupings (hidden from user initially)
- `created_at: datetime` - Puzzle creation timestamp
- `difficulty_level: str` - Overall puzzle difficulty ("easy", "medium", "hard", "expert")

**Validation Rules**:
- Must have exactly 16 words
- Must have exactly 4 groups
- Each word must belong to exactly one group
- All words across groups must be unique

**State Transitions**: 
- Created → Active (when user starts)
- Active → Completed (when all groups found)
- Active → Failed (when 4 incorrect guesses made)

### Word
**Purpose**: Individual puzzle element with display text and group membership
**Fields**:
- `text: str` - The display word (e.g., "BASS", "PIANO")
- `group_id: str` - Reference to the Group this word belongs to
- `position: int` - Original position in 16-word grid (0-15)

**Validation Rules**:
- `text` must be non-empty, alphanumeric plus common punctuation
- `text` length must be <= 20 characters
- `group_id` must reference valid Group
- `position` must be unique within puzzle (0-15)

### Group
**Purpose**: A set of 4 related words with common theme/connection
**Fields**:
- `id: str` - Unique group identifier
- `theme: str` - The connection description (e.g., "Types of Fish", "Musical Instruments")
- `difficulty: str` - Group difficulty level ("yellow", "green", "blue", "purple")
- `words: List[Word]` - Exactly 4 words in this group
- `is_solved: bool` - Whether user has correctly identified this group

**Validation Rules**:
- Must have exactly 4 words
- `theme` must be descriptive (3-50 characters)
- `difficulty` must be one of the 4 standard NYT levels
- All words in group must have matching `group_id`

**State Transitions**:
- Unsolved → Solved (when user correctly guesses all 4 words)

### Guess
**Purpose**: Records a user's attempt to identify a word group
**Fields**:
- `id: str` - Unique guess identifier
- `session_id: str` - Reference to user session
- `selected_words: List[str]` - The 4 words user selected (word text)
- `timestamp: datetime` - When guess was made
- `result: str` - Guess outcome ("correct", "incorrect", "one_away")
- `matched_group_id: str | None` - Group ID if correct, None if incorrect
- `ai_recommendation_id: str | None` - Which AI recommendation influenced this guess

**Validation Rules**:
- Must have exactly 4 selected words
- `selected_words` must all exist in current puzzle
- `result` must be one of the 3 valid outcomes
- If `result` is "correct", `matched_group_id` must be provided
- `timestamp` must be within active session timeframe

**State Transitions**:
- Submitted → Validated → Result Determined (immutable after creation)

### Session
**Purpose**: Tracks user's current puzzle-solving session and progress
**Fields**:
- `id: str` - Unique session identifier
- `puzzle_id: str` - Reference to active puzzle
- `user_id: str | None` - User identifier (None for anonymous sessions)
- `start_time: datetime` - Session start timestamp
- `last_activity: datetime` - Most recent user action
- `status: str` - Current session state ("active", "completed", "failed", "abandoned")
- `solved_groups: List[str]` - List of solved group IDs
- `remaining_words: List[str]` - Words still available for guessing
- `incorrect_guess_count: int` - Number of incorrect guesses made (max 4)
- `guess_history: List[Guess]` - All guesses made in this session

**Validation Rules**:
- `incorrect_guess_count` must be 0-4
- `solved_groups` length must be 0-4
- `remaining_words` + words in `solved_groups` must equal 16
- `guess_history` must be chronologically ordered

**State Transitions**:
- Created → Active (first guess made)
- Active → Completed (all 4 groups solved)
- Active → Failed (4 incorrect guesses reached)
- Active → Abandoned (timeout or explicit abandonment)

### AIRecommendation
**Purpose**: Stores LLM-generated word grouping suggestions for user assistance
**Fields**:
- `id: str` - Unique recommendation identifier
- `session_id: str` - Reference to session this recommendation was for
- `puzzle_state: List[str]` - Available words when recommendation requested
- `recommendations: List[RecommendationGroup]` - Suggested groupings
- `confidence_scores: Dict[str, float]` - Confidence per recommendation (0.0-1.0)
- `timestamp: datetime` - When recommendation was generated
- `llm_model: str` - Which LLM model generated this (e.g., "gpt-4")
- `processing_time_ms: int` - Time taken to generate recommendation

**Validation Rules**:
- `puzzle_state` must contain 4-16 words (depending on game progress)
- `recommendations` must suggest valid groupings from `puzzle_state` words
- `confidence_scores` values must be 0.0-1.0
- `processing_time_ms` must be positive integer

### RecommendationGroup
**Purpose**: Individual word grouping suggestion within an AIRecommendation
**Fields**:
- `words: List[str]` - The 4 words recommended to group together
- `explanation: str` - LLM's reasoning for this grouping
- `confidence: float` - LLM's confidence in this grouping (0.0-1.0)

**Validation Rules**:
- Must have exactly 4 words
- `explanation` must be 10-200 characters
- `confidence` must be 0.0-1.0
- `words` must all exist in the puzzle state

## Entity Relationships

```
Puzzle (1) ←→ (4) Group
Puzzle (1) ←→ (16) Word
Group (1) ←→ (4) Word
Session (1) ←→ (1) Puzzle
Session (1) ←→ (0-12) Guess
Session (1) ←→ (0-*) AIRecommendation
AIRecommendation (1) ←→ (1-4) RecommendationGroup
Guess (0-1) ←→ (1) AIRecommendation
```

## State Management

### Puzzle Lifecycle
1. **Created**: Puzzle instantiated with 16 words in 4 groups
2. **Active**: User session started, guesses being made
3. **Completed**: All 4 groups correctly identified
4. **Failed**: 4 incorrect guesses exhausted

### Session State Flow
1. **Initialize**: Create session with full puzzle (16 words available)
2. **Guess Loop**: User selects 4 words → Submit guess → Update state
3. **Correct Guess**: Remove 4 words from available, mark group solved
4. **Incorrect Guess**: Increment incorrect count, words remain available
5. **Terminal States**: Completed (4 groups solved) or Failed (4 incorrect)

### Data Consistency Rules
- `Session.remaining_words` = Original 16 words - words in `solved_groups`
- `Session.incorrect_guess_count` = count of "incorrect" + "one_away" guesses
- `Group.is_solved` = true iff group ID in `Session.solved_groups`
- `AIRecommendation.puzzle_state` must match `Session.remaining_words` at time of request

## Serialization Schemas

All entities serialize to JSON for API transport. Field names use snake_case in Python models and camelCase in TypeScript interfaces.

### API Response DTOs
- Entities may be serialized differently for API responses (e.g., hide `Group.theme` until solved)
- Puzzle responses exclude solution information during active gameplay
- Session responses include computed fields like `can_make_guess: bool`
