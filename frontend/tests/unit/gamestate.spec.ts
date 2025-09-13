import GameStateManager from '../../src/services/GameState';

describe('GameStateManager', () => {
  test('addRecommendation and updateEvaluation', () => {
    const gm = new GameStateManager();
    const rec: any = {
      id: 'r1',
      sessionId: 's1',
      recommendedWords: ['A','B','C','D'],
      explanation: 'x',
      timestamp: new Date().toISOString(),
      llmModel: 'gpt-test',
      processingTimeMs: 10
    };

    gm.addRecommendation(rec);
    expect(gm.getRecommendationHistory().length).toBeGreaterThan(0);

    gm.updateRecommendationEvaluation('r1', 'correct');
    const current = gm.getCurrentRecommendation();
    expect(current).not.toBeNull();
    expect(current!.userEvaluation).toBe('correct');
  });
});
