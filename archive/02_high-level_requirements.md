# High-Level Requirements: NYT Connections Puzzle Assistant Web Application

## 1. Purpose

Develop a web application that assists users in solving the New York Times Connections Puzzle. The application leverages a Large Language Model (LLM) to generate recommendations for grouping words and tracks invalid guesses to enhance the solving experience.

## 2. Functional Requirements

### 2.1 User Interface
- Display the current set of puzzle words (16 words).
- Allow users to select and group words into sets of four.
- Show previous guesses, indicating which were invalid.
- Provide an interface for users to submit guesses and receive feedback.
- Display LLM-generated recommendations for possible word groupings.

### 2.2 LLM Integration
- Send the current puzzle state to the LLM.
- Receive and display recommended groupings from the LLM.
- Allow users to request new recommendations after each guess.

### 2.3 Guess Tracking
- Record each LLM guess, including the selected words and the result (valid/invalid).
- Visually distinguish invalid guesses from valid ones.
- Allow users to review the LLM guess history.

### 2.4 Puzzle Progression
- Update the puzzle state as groups are correctly identified.
- Indicate solved groups and remaining words.
- Allow users to reset the puzzle or start a new one.

## 3. Non-Functional Requirements

- **Performance:** Recommendations and UI updates should occur within 2 seconds.
- **Usability:** The interface should be intuitive and accessible on desktop devices.
- **Reliability:** The application should not lose user progress due to accidental refresh or navigation.
- **Security:** User data and puzzle history should be stored securely.

## 4. Out of Scope

- Automated solving of the puzzle without user interaction.
- Support for puzzles other than the NYT Connections format.
