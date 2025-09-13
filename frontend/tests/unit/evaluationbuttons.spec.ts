import { EvaluationButtons } from '../../src/components/EvaluationButtons';

describe('EvaluationButtons', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement('div');
    container.id = 'eval-btn-test';
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  test('keyboard shortcuts trigger evaluation', () => {
    const evals = new EvaluationButtons('eval-btn-test');
    // make a fake recommendation id
    evals.setRecommendation('rec1');

    // Simulate keyboard event for 'C' (Correct)
    const ev = new KeyboardEvent('keydown', { key: 'c' });
    document.dispatchEvent(ev);

    // The component stores last evaluation; assert it is set
    const last = evals.getLastEvaluation();
    expect(last).not.toBeNull();
    expect(last!.recommendationId).toBe('rec1');
  });
});
