# Frontend Testing Guide

This document explains how to run the existing tests for the frontend, how the project is structured for testing, and gives quick examples for writing unit tests for the main DOM components.

Prerequisites
- Node.js and npm installed (the project uses the `frontend` folder's package.json).

Install dependencies
```bash
cd frontend
npm install
```

Run unit tests (Jest)
```bash
cd frontend
npm test
```

Run Playwright end-to-end tests
```bash
cd frontend
npm run test:e2e
```

Start dev server for manual testing
```bash
cd frontend
npm run dev
# open the dev URL shown by webpack-dev-server (usually http://localhost:8080)
```

What to test (high-value components)
- `FileUpload` (src/components/FileUpload.ts)
  - parseFile / extractWords behavior for CSV/TXT input
  - validateFile rejects invalid types and sizes
  - simulateUpload timing and onFileUploaded callback

- `PuzzleView` (src/components/PuzzleView.ts)
  - selection toggling and selection limit (4)
  - action bar state (submit enabled only when 4 selected)
  - highlightRecommendation auto-selects words

- `RecommendationCard` (src/components/RecommendationCard.ts)
  - showRecommendation renders recommended words and metadata
  - evaluation flow triggers `onEvaluate` callback and updates UI

- `EvaluationButtons`, `SessionStatus`, `HistoryView` — test keyboard shortcuts, timer updates, filtering/sorting logic.

Example unit test patterns

1) Create a DOM container and instantiate the component

```ts
// Example: tests/unit/fileupload.spec.ts
import { FileUpload } from '../../src/components/FileUpload';

test('extractWords parses common delimiters', async () => {
  const container = document.createElement('div');
  container.id = 'test-upload';
  document.body.appendChild(container);

  const uploader = new FileUpload('test-upload');

  const content = 'BASS,PIANO\nGUITAR;DRUMS';
  const words = (uploader as any).extractWords(content);
  expect(words).toEqual(['BASS','PIANO','GUITAR','DRUMS']);
});
```

2) Simulate user interactions by dispatching DOM events

```ts
// Example: selecting words in PuzzleView
import { PuzzleView } from '../../src/components/PuzzleView';

test('selecting four words enables submit', () => {
  const container = document.createElement('div');
  container.id = 'puzzle-test';
  document.body.appendChild(container);

  const puzzle = new PuzzleView('puzzle-test');
  puzzle.updatePuzzle({ puzzleId: 'p1', remainingWords: ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'], solvedGroups: [] });

  // Programmatically select words
  puzzle.selectWords(['A','B','C','D']);
  expect(puzzle.getSelectedWords().length).toBe(4);
  // Submit button should be enabled in the DOM
  const submitBtn = container.querySelector('#submit-btn') as HTMLButtonElement;
  expect(submitBtn.disabled).toBe(false);
});
```

Notes and tips
- Jest runs in a JSDOM environment by default — DOM APIs like document.createElement work out of the box.
- When testing timers (simulateUpload, periodic updates), use Jest fake timers (jest.useFakeTimers()) and advance timers.
- For services (ApiService, WebSocketService), mock network calls. For unit tests, mock `fetch` or replace `webSocketService` with a test double.
- Keep tests small and deterministic: prefer calling component methods directly (e.g., `selectWords`, `showRecommendation`) instead of relying on complex DOM interactions unless doing an integration/E2E test.

Where to add tests
- Unit tests: `frontend/tests/unit/*.spec.ts` (create this folder if it doesn't exist)
- E2E tests are in `frontend/tests/e2e` (Playwright)

If you'd like, I can scaffold a few unit test files for `FileUpload`, `PuzzleView`, and `RecommendationCard` and run them locally. Reply with which components to scaffold first.

---
Requirements coverage
- Create `frontend/TESTING.md` with commands and examples — Done

