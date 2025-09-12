/**
 * EvaluationButtons component for NYT Connections Puzzle Assistant
 * 
 * Provides user evaluation options for AI recommendations.
 * Handles correct, incorrect, and one-away feedback.
 */

// Evaluation types
type EvaluationType = 'correct' | 'incorrect' | 'one_away';

// Evaluation button configuration
interface EvaluationButtonConfig {
    type: EvaluationType;
    label: string;
    icon: string;
    description: string;
    className: string;
    shortcut?: string;
}

// Evaluation result interface
interface EvaluationResult {
    type: EvaluationType;
    recommendationId: string;
    timestamp: Date;
    confidence?: number;
}

// Evaluation callbacks
interface EvaluationButtonsCallbacks {
    onEvaluate?: (result: EvaluationResult) => void;
    onBeforeEvaluate?: (type: EvaluationType) => boolean; // Return false to cancel
    onAfterEvaluate?: (result: EvaluationResult) => void;
}

/**
 * EvaluationButtons component class for handling user feedback on recommendations
 */
export class EvaluationButtons {
    private container: HTMLElement;
    private callbacks: EvaluationButtonsCallbacks;
    private currentRecommendationId: string | null = null;
    private isEnabled: boolean = true;
    private lastEvaluation: EvaluationResult | null = null;

    private readonly buttonConfigs: EvaluationButtonConfig[] = [
        {
            type: 'correct',
            label: 'Correct',
            icon: '✓',
            description: 'This recommendation led to a correct group',
            className: 'btn-success',
            shortcut: 'C'
        },
        {
            type: 'one_away',
            label: 'One Away',
            icon: '~',
            description: 'Three of the four words are in a group',
            className: 'btn-warning',
            shortcut: 'O'
        },
        {
            type: 'incorrect',
            label: 'Incorrect',
            icon: '✗',
            description: 'This recommendation was not helpful',
            className: 'btn-danger',
            shortcut: 'I'
        }
    ];

    constructor(containerId: string, callbacks?: EvaluationButtonsCallbacks) {
        this.container = document.getElementById(containerId) || document.body;
        this.callbacks = callbacks || {};
        
        this.createElements();
        this.setupEventListeners();
    }

    /**
     * Create the DOM elements for the evaluation buttons
     */
    private createElements(): void {
        this.container.className = 'evaluation-buttons-container';
        this.container.innerHTML = `
            <div class="evaluation-section">
                <div class="evaluation-header">
                    <h3 class="evaluation-title">Evaluate AI Recommendation</h3>
                    <p class="evaluation-subtitle">Help improve future recommendations by providing feedback</p>
                </div>
                
                <div class="evaluation-buttons">
                    ${this.buttonConfigs.map(config => this.createButtonHTML(config)).join('')}
                </div>
                
                <div class="evaluation-info">
                    <div class="shortcuts-info">
                        <span class="shortcuts-label">Keyboard shortcuts:</span>
                        ${this.buttonConfigs.map(config => 
                            config.shortcut ? `<kbd>${config.shortcut}</kbd> ${config.label}` : ''
                        ).filter(Boolean).join(' • ')}
                    </div>
                </div>
                
                <div class="evaluation-status"></div>
            </div>
        `;

        // Initially hide the component
        this.hide();
    }

    /**
     * Create HTML for a single evaluation button
     */
    private createButtonHTML(config: EvaluationButtonConfig): string {
        return `
            <button class="btn evaluation-btn ${config.className}" 
                    data-type="${config.type}"
                    data-shortcut="${config.shortcut || ''}"
                    title="${config.description}">
                <span class="btn-icon">${config.icon}</span>
                <span class="btn-label">${config.label}</span>
                <span class="btn-description">${config.description}</span>
            </button>
        `;
    }

    /**
     * Set up event listeners
     */
    private setupEventListeners(): void {
        // Button clicks
        this.container.addEventListener('click', (e) => {
            const button = (e.target as HTMLElement).closest('.evaluation-btn');
            if (button) {
                const type = button.getAttribute('data-type') as EvaluationType;
                this.handleEvaluation(type);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (!this.isEnabled || !this.currentRecommendationId) return;

            const key = e.key.toUpperCase();
            const config = this.buttonConfigs.find(c => c.shortcut === key);
            
            if (config && !e.ctrlKey && !e.metaKey && !e.altKey) {
                // Only trigger if no modifier keys and not in an input
                const target = e.target as HTMLElement;
                if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    this.handleEvaluation(config.type);
                }
            }
        });

        // Hover effects for better UX
        this.container.addEventListener('mouseenter', (e) => {
            const button = (e.target as HTMLElement).closest('.evaluation-btn');
            if (button) {
                this.showButtonPreview(button.getAttribute('data-type') as EvaluationType);
            }
        }, true);

        this.container.addEventListener('mouseleave', (e) => {
            const button = (e.target as HTMLElement).closest('.evaluation-btn');
            if (button) {
                this.hideButtonPreview();
            }
        }, true);
    }

    /**
     * Handle evaluation button click or keyboard shortcut
     */
    private handleEvaluation(type: EvaluationType): void {
        if (!this.isEnabled || !this.currentRecommendationId) return;

        // Call before evaluation callback
        const shouldContinue = this.callbacks.onBeforeEvaluate?.(type) !== false;
        if (!shouldContinue) return;

        // Create evaluation result
        const result: EvaluationResult = {
            type,
            recommendationId: this.currentRecommendationId,
            timestamp: new Date()
        };

        // Store last evaluation
        this.lastEvaluation = result;

        // Visual feedback
        this.showEvaluationFeedback(type);

        // Update button states
        this.updateButtonStates(type);

        // Call callbacks
        this.callbacks.onEvaluate?.(result);
        this.callbacks.onAfterEvaluate?.(result);

        // Show success message
        this.showEvaluationSuccess(type);
    }

    /**
     * Show evaluation feedback with animation
     */
    private showEvaluationFeedback(type: EvaluationType): void {
        const button = this.container.querySelector(`[data-type="${type}"]`);
        if (button) {
            button.classList.add('evaluated', 'animate-evaluation');
            
            // Remove animation class after animation completes
            setTimeout(() => {
                button.classList.remove('animate-evaluation');
            }, 300);
        }
    }

    /**
     * Update button states after evaluation
     */
    private updateButtonStates(selectedType: EvaluationType): void {
        this.buttonConfigs.forEach(config => {
            const button = this.container.querySelector(`[data-type="${config.type}"]`);
            if (button) {
                if (config.type === selectedType) {
                    button.classList.add('selected', 'evaluated');
                } else {
                    button.classList.add('disabled');
                    (button as HTMLButtonElement).disabled = true;
                }
            }
        });
    }

    /**
     * Show button preview on hover
     */
    private showButtonPreview(type: EvaluationType): void {
        const config = this.buttonConfigs.find(c => c.type === type);
        if (config) {
            const statusElement = this.container.querySelector('.evaluation-status');
            if (statusElement) {
                statusElement.className = 'evaluation-status preview';
                statusElement.innerHTML = `
                    <span class="preview-icon">${config.icon}</span>
                    <span class="preview-text">${config.description}</span>
                `;
            }
        }
    }

    /**
     * Hide button preview
     */
    private hideButtonPreview(): void {
        const statusElement = this.container.querySelector('.evaluation-status');
        if (statusElement && statusElement.classList.contains('preview')) {
            statusElement.className = 'evaluation-status';
            statusElement.innerHTML = '';
        }
    }

    /**
     * Show evaluation success message
     */
    private showEvaluationSuccess(type: EvaluationType): void {
        const config = this.buttonConfigs.find(c => c.type === type);
        if (!config) return;

        const statusElement = this.container.querySelector('.evaluation-status');
        if (statusElement) {
            statusElement.className = `evaluation-status success ${type}`;
            statusElement.innerHTML = `
                <span class="success-icon">${config.icon}</span>
                <span class="success-text">
                    Evaluation recorded: ${config.label}
                </span>
                <span class="success-details">
                    Thank you for helping improve the AI!
                </span>
            `;

            // Clear success message after delay
            setTimeout(() => {
                statusElement.className = 'evaluation-status';
                statusElement.innerHTML = '';
            }, 3000);
        }
    }

    /**
     * Set the current recommendation to evaluate
     */
    public setRecommendation(recommendationId: string): void {
        this.currentRecommendationId = recommendationId;
        this.lastEvaluation = null;
        this.resetButtonStates();
        this.show();
    }

    /**
     * Reset button states to initial state
     */
    private resetButtonStates(): void {
        this.buttonConfigs.forEach(config => {
            const button = this.container.querySelector(`[data-type="${config.type}"]`);
            if (button) {
                button.classList.remove('selected', 'evaluated', 'disabled');
                (button as HTMLButtonElement).disabled = false;
            }
        });
    }

    /**
     * Show the evaluation buttons
     */
    public show(): void {
        this.container.style.display = 'block';
        this.container.classList.add('visible');
    }

    /**
     * Hide the evaluation buttons
     */
    public hide(): void {
        this.container.style.display = 'none';
        this.container.classList.remove('visible');
    }

    /**
     * Enable or disable the evaluation buttons
     */
    public setEnabled(enabled: boolean): void {
        this.isEnabled = enabled;
        
        const buttons = this.container.querySelectorAll('.evaluation-btn');
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
     * Check if buttons are currently enabled
     */
    public isButtonsEnabled(): boolean {
        return this.isEnabled;
    }

    /**
     * Get the last evaluation result
     */
    public getLastEvaluation(): EvaluationResult | null {
        return this.lastEvaluation;
    }

    /**
     * Check if current recommendation has been evaluated
     */
    public isEvaluated(): boolean {
        return this.lastEvaluation !== null;
    }

    /**
     * Clear current recommendation and hide buttons
     */
    public clear(): void {
        this.currentRecommendationId = null;
        this.lastEvaluation = null;
        this.resetButtonStates();
        this.hide();
    }

    /**
     * Set evaluation programmatically (for external updates)
     */
    public setEvaluation(type: EvaluationType, recommendationId: string): void {
        if (this.currentRecommendationId === recommendationId) {
            const result: EvaluationResult = {
                type,
                recommendationId,
                timestamp: new Date()
            };
            
            this.lastEvaluation = result;
            this.updateButtonStates(type);
            this.showEvaluationSuccess(type);
        }
    }

    /**
     * Get available evaluation types
     */
    public getEvaluationTypes(): EvaluationType[] {
        return this.buttonConfigs.map(config => config.type);
    }

    /**
     * Get button configuration for a specific type
     */
    public getButtonConfig(type: EvaluationType): EvaluationButtonConfig | undefined {
        return this.buttonConfigs.find(config => config.type === type);
    }

    /**
     * Show custom message in status area
     */
    public showMessage(message: string, type: 'info' | 'warning' | 'error' = 'info'): void {
        const statusElement = this.container.querySelector('.evaluation-status');
        if (statusElement) {
            statusElement.className = `evaluation-status message ${type}`;
            statusElement.textContent = message;

            // Clear message after delay
            setTimeout(() => {
                statusElement.className = 'evaluation-status';
                statusElement.innerHTML = '';
            }, 5000);
        }
    }

    /**
     * Add custom evaluation type (for extensibility)
     */
    public addCustomEvaluation(config: EvaluationButtonConfig): void {
        this.buttonConfigs.push(config);
        this.createElements(); // Recreate with new button
        this.setupEventListeners();
    }
}

// Export types and interfaces for use by other components
export { 
    EvaluationType, 
    EvaluationButtonConfig, 
    EvaluationResult, 
    EvaluationButtonsCallbacks 
};
