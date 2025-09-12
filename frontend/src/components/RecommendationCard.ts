/**
 * RecommendationCard component for NYT Connections Puzzle Assistant
 * 
 * Displays AI-generated recommendations with explanations and
 * provides user evaluation options.
 */

// Recommendation data interface
interface Recommendation {
    id: string;
    sessionId: string;
    recommendedWords: string[];
    explanation: string;
    timestamp: Date;
    userEvaluation?: 'correct' | 'incorrect' | 'one_away';
    evaluationTimestamp?: Date;
    llmModel: string;
    processingTimeMs: number;
}

// Recommendation card callbacks
interface RecommendationCardCallbacks {
    onEvaluate?: (recommendationId: string, evaluation: 'correct' | 'incorrect' | 'one_away') => void;
    onWordsHighlight?: (words: string[]) => void;
    onWordsSelect?: (words: string[]) => void;
    onClearHighlight?: () => void;
}

/**
 * RecommendationCard component class for displaying AI recommendations
 */
export class RecommendationCard {
    private container: HTMLElement;
    private recommendation: Recommendation | null = null;
    private callbacks: RecommendationCardCallbacks;
    private cardElement: HTMLElement | null = null;

    constructor(containerId: string, callbacks?: RecommendationCardCallbacks) {
        this.container = document.getElementById(containerId) || document.body;
        this.callbacks = callbacks || {};
        
        this.createElements();
    }

    /**
     * Create the DOM elements for the recommendation card
     */
    private createElements(): void {
        this.container.className = 'recommendation-card-container';
        this.container.innerHTML = `
            <div class="recommendation-placeholder">
                <div class="placeholder-content">
                    <div class="placeholder-icon">🤖</div>
                    <div class="placeholder-text">
                        <p>Click "Get Recommendation" to receive AI suggestions</p>
                        <p class="placeholder-subtitle">The AI will analyze remaining words and suggest potential groups</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Display a new recommendation
     */
    public showRecommendation(recommendation: Recommendation): void {
        this.recommendation = recommendation;
        this.renderRecommendationCard();
    }

    /**
     * Render the recommendation card
     */
    private renderRecommendationCard(): void {
        if (!this.recommendation) return;

        const isEvaluated = !!this.recommendation.userEvaluation;
        const evaluationClass = this.recommendation.userEvaluation ? 
            `evaluated-${this.recommendation.userEvaluation}` : '';

        this.container.innerHTML = `
            <div class="recommendation-card ${evaluationClass}">
                <div class="recommendation-header">
                    <div class="recommendation-title">
                        <span class="ai-icon">🤖</span>
                        AI Recommendation
                    </div>
                    <div class="recommendation-meta">
                        <span class="model-name">${this.recommendation.llmModel}</span>
                        <span class="processing-time">${this.recommendation.processingTimeMs}ms</span>
                        <span class="timestamp">${this.formatTimestamp(this.recommendation.timestamp)}</span>
                    </div>
                </div>

                <div class="recommendation-content">
                    <div class="recommended-words">
                        <div class="words-label">Recommended Group:</div>
                        <div class="words-list">
                            ${this.recommendation.recommendedWords.map(word => 
                                `<span class="recommended-word">${word}</span>`
                            ).join('')}
                        </div>
                    </div>

                    <div class="explanation">
                        <div class="explanation-label">AI Explanation:</div>
                        <div class="explanation-text">${this.recommendation.explanation}</div>
                    </div>
                </div>

                ${this.renderEvaluationSection()}

                <div class="recommendation-actions">
                    <button class="btn btn-outline highlight-btn" 
                            ${isEvaluated ? 'disabled' : ''}>
                        Highlight Words
                    </button>
                    <button class="btn btn-outline select-btn"
                            ${isEvaluated ? 'disabled' : ''}>
                        Select Words
                    </button>
                    <button class="btn btn-outline clear-btn">
                        Clear Highlight
                    </button>
                </div>
            </div>
        `;

        this.cardElement = this.container.querySelector('.recommendation-card');
        this.setupCardEventListeners();
    }

    /**
     * Render the evaluation section based on current state
     */
    private renderEvaluationSection(): string {
        if (!this.recommendation) return '';

        if (this.recommendation.userEvaluation) {
            // Show evaluation result
            const evaluationText = this.getEvaluationDisplayText(this.recommendation.userEvaluation);
            const evaluationIcon = this.getEvaluationIcon(this.recommendation.userEvaluation);
            
            return `
                <div class="evaluation-result">
                    <div class="evaluation-display">
                        <span class="evaluation-icon">${evaluationIcon}</span>
                        <span class="evaluation-text">${evaluationText}</span>
                        ${this.recommendation.evaluationTimestamp ? 
                            `<span class="evaluation-time">
                                ${this.formatTimestamp(this.recommendation.evaluationTimestamp)}
                            </span>` : ''
                        }
                    </div>
                </div>
            `;
        } else {
            // Show evaluation buttons
            return `
                <div class="evaluation-section">
                    <div class="evaluation-label">How was this recommendation?</div>
                    <div class="evaluation-buttons">
                        <button class="btn btn-success evaluate-btn" data-evaluation="correct">
                            ✓ Correct
                        </button>
                        <button class="btn btn-warning evaluate-btn" data-evaluation="one_away">
                            ~ One Away
                        </button>
                        <button class="btn btn-danger evaluate-btn" data-evaluation="incorrect">
                            ✗ Incorrect
                        </button>
                    </div>
                    <div class="evaluation-help">
                        <small>Help the AI learn by evaluating its recommendations</small>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Set up event listeners for the card
     */
    private setupCardEventListeners(): void {
        if (!this.cardElement) return;

        // Evaluation buttons
        const evaluateButtons = this.cardElement.querySelectorAll('.evaluate-btn');
        evaluateButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const evaluation = (e.target as HTMLElement).dataset.evaluation as 'correct' | 'incorrect' | 'one_away';
                this.handleEvaluation(evaluation);
            });
        });

        // Action buttons
        const highlightBtn = this.cardElement.querySelector('.highlight-btn');
        const selectBtn = this.cardElement.querySelector('.select-btn');
        const clearBtn = this.cardElement.querySelector('.clear-btn');

        highlightBtn?.addEventListener('click', () => this.highlightWords());
        selectBtn?.addEventListener('click', () => this.selectWords());
        clearBtn?.addEventListener('click', () => this.clearHighlight());
    }

    /**
     * Handle evaluation button click
     */
    private handleEvaluation(evaluation: 'correct' | 'incorrect' | 'one_away'): void {
        if (!this.recommendation) return;

        // Update recommendation object
        this.recommendation.userEvaluation = evaluation;
        this.recommendation.evaluationTimestamp = new Date();

        // Re-render to show evaluation result
        this.renderRecommendationCard();

        // Notify callback
        this.callbacks.onEvaluate?.(this.recommendation.id, evaluation);

        // Show feedback message
        this.showEvaluationFeedback(evaluation);
    }

    /**
     * Highlight recommended words in the puzzle
     */
    private highlightWords(): void {
        if (this.recommendation) {
            this.callbacks.onWordsHighlight?.(this.recommendation.recommendedWords);
        }
    }

    /**
     * Select recommended words in the puzzle
     */
    private selectWords(): void {
        if (this.recommendation) {
            this.callbacks.onWordsSelect?.(this.recommendation.recommendedWords);
        }
    }

    /**
     * Clear word highlights
     */
    private clearHighlight(): void {
        this.callbacks.onClearHighlight?.();
    }

    /**
     * Show evaluation feedback message
     */
    private showEvaluationFeedback(evaluation: 'correct' | 'incorrect' | 'one_away'): void {
        const messages = {
            correct: 'Great! Thanks for confirming this recommendation was correct.',
            incorrect: 'Thanks for the feedback. The AI will learn from this.',
            one_away: 'Close! This helps the AI understand partial matches.'
        };

        // Create temporary feedback message
        const feedback = document.createElement('div');
        feedback.className = `evaluation-feedback ${evaluation}`;
        feedback.textContent = messages[evaluation];

        this.cardElement?.appendChild(feedback);

        // Remove after 3 seconds
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }

    /**
     * Get display text for evaluation
     */
    private getEvaluationDisplayText(evaluation: string): string {
        const displayTexts = {
            correct: 'Marked as Correct',
            incorrect: 'Marked as Incorrect', 
            one_away: 'Marked as One Away'
        };
        return displayTexts[evaluation as keyof typeof displayTexts] || evaluation;
    }

    /**
     * Get icon for evaluation
     */
    private getEvaluationIcon(evaluation: string): string {
        const icons = {
            correct: '✅',
            incorrect: '❌',
            one_away: '⚠️'
        };
        return icons[evaluation as keyof typeof icons] || '?';
    }

    /**
     * Format timestamp for display
     */
    private formatTimestamp(timestamp: Date): string {
        const now = new Date();
        const diff = now.getTime() - timestamp.getTime();
        const minutes = Math.floor(diff / (1000 * 60));
        const hours = Math.floor(diff / (1000 * 60 * 60));

        if (minutes < 1) {
            return 'just now';
        } else if (minutes < 60) {
            return `${minutes}m ago`;
        } else if (hours < 24) {
            return `${hours}h ago`;
        } else {
            return timestamp.toLocaleDateString();
        }
    }

    /**
     * Update evaluation status of current recommendation
     */
    public updateEvaluation(evaluation: 'correct' | 'incorrect' | 'one_away'): void {
        if (this.recommendation) {
            this.recommendation.userEvaluation = evaluation;
            this.recommendation.evaluationTimestamp = new Date();
            this.renderRecommendationCard();
        }
    }

    /**
     * Check if current recommendation is evaluated
     */
    public isEvaluated(): boolean {
        return !!this.recommendation?.userEvaluation;
    }

    /**
     * Get current recommendation
     */
    public getCurrentRecommendation(): Recommendation | null {
        return this.recommendation;
    }

    /**
     * Clear the current recommendation
     */
    public clear(): void {
        this.recommendation = null;
        this.createElements();
    }

    /**
     * Show loading state while waiting for recommendation
     */
    public showLoading(): void {
        this.container.innerHTML = `
            <div class="recommendation-loading">
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">
                        <p>AI is analyzing the puzzle...</p>
                        <p class="loading-subtitle">This may take a moment</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Show error state
     */
    public showError(message: string = 'Failed to get recommendation'): void {
        this.container.innerHTML = `
            <div class="recommendation-error">
                <div class="error-content">
                    <div class="error-icon">⚠️</div>
                    <div class="error-text">
                        <p>${message}</p>
                        <p class="error-subtitle">Please try again</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Enable or disable interaction
     */
    public setEnabled(enabled: boolean): void {
        const buttons = this.container.querySelectorAll('button');
        buttons.forEach(button => {
            (button as HTMLButtonElement).disabled = !enabled;
        });

        if (enabled) {
            this.container.classList.remove('disabled');
        } else {
            this.container.classList.add('disabled');
        }
    }

    /**
     * Set highlight on/off for recommended words
     */
    public setWordsHighlighted(highlighted: boolean): void {
        if (this.cardElement) {
            if (highlighted) {
                this.cardElement.classList.add('words-highlighted');
            } else {
                this.cardElement.classList.remove('words-highlighted');
            }
        }
    }
}

// Export interfaces for use by other components
export { Recommendation, RecommendationCardCallbacks };
