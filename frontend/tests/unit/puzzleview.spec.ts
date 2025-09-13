import { PuzzleView } from '../../src/components/PuzzleView';

describe('PuzzleView', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement('div');
    container.id = 'puzzle-test';
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  test('selecting four words enables submit', () => {
    const puzzle = new PuzzleView('puzzle-test');
    puzzle.updatePuzzle({ puzzleId: 'p1', remainingWords: ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'], solvedGroups: [] });

    puzzle.selectWords(['A','B','C','D']);
    expect(puzzle.getSelectedWords().length).toBe(4);

    const submitBtn = container.querySelector('#submit-btn') as HTMLButtonElement;
    expect(submitBtn.disabled).toBe(false);
  });
});
