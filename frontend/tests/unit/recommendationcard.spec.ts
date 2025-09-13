import { RecommendationCard } from '../../src/components/RecommendationCard';

describe('RecommendationCard', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement('div');
    container.id = 'rec-card-test';
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  test('showRecommendation renders words and metadata', () => {
    const card = new RecommendationCard('rec-card-test');
    const mockRec: any = {
      id: 'r1',
      sessionId: 's1',
      recommendedWords: ['A','B','C','D'],
      explanation: 'Because they are instruments',
      timestamp: new Date(),
      llmModel: 'gpt-test',
      processingTimeMs: 123
    };

    card.showRecommendation(mockRec);
    const words = container.querySelectorAll('.recommended-word');
    expect(words.length).toBe(4);
  });
});
