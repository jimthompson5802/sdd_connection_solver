/**
 * PuzzleView component for NYT Connections Puzzle Assistant
 * 
 * Displays the current puzzle state including remaining words,
 * solved groups, and provides interactive word selection.
 */

// Puzzle data interfaces
interface Word {
    word: string;
    isSelected: boolean;
    isInSolvedGroup: boolean;
    groupId?: string;
}

interface SolvedGroup {
    id: string;
    theme: string;
    words: string[];
    difficulty: string;
    color: string;
}

interface PuzzleState {
    puzzleId: string;
    remainingWords: string[];
    solvedGroups: SolvedGroup[];
    selectedWords: string[];
    maxSelections: number;
}

// Puzzle view callbacks
interface PuzzleViewCallbacks {
    onWordSelected?: (word: string, isSelected: boolean) => void;
    onSelectionChanged?: (selectedWords: string[]) => void;
    onRequestRecommendation?: () => void;
    onSubmitGroup?: (words: string[]) => void;
}

/**
 * PuzzleView component class for displaying puzzle state and handling word selection
 */
export class PuzzleView {
    private container: HTMLElement;
    private puzzleState: PuzzleState;
    private callbacks: PuzzleViewCallbacks;
    private wordsGrid: HTMLElement | null = null;
    private solvedGroupsContainer: HTMLElement | null = null;
    private actionBar: HTMLElement | null = null;

    constructor(containerId: string, callbacks?: PuzzleViewCallbacks) {
        this.container = document.getElementById(containerId) || document.body;
        this.callbacks = callbacks || {};
        this.puzzleState = {
            puzzleId: '',
            remainingWords: [],
            solvedGroups: [],
            selectedWords: [],
            maxSelections: 4
        };

        this.createElements();
        this.setupEventListeners();
    }

    /**
     * Create the DOM elements for the puzzle view
     */
    private createElements(): void {
        this.container.className = 'puzzle-view-container';
        this.container.innerHTML = `
            <div class="puzzle-header">
                <h2>NYT Connections Puzzle</h2>
                <div class="puzzle-instructions">
                    Find groups of four items that share something in common.
                </div>
            </div>
            
            <div class="solved-groups-container"></div>
            
            <div class="words-grid"></div>
            
            <div class="action-bar">
                <div class="selection-info">
                    <span class="selection-count">0</span> of 4 words selected
                </div>
                <div class="action-buttons">
                    <button class="btn btn-secondary" id="shuffle-btn">Shuffle</button>
                    <button class="btn btn-secondary" id="deselect-btn" disabled>Deselect All</button>
                    <button class="btn btn-primary" id="recommend-btn">Get Recommendation</button>
                    <button class="btn btn-primary" id="submit-btn" disabled>Submit</button>
                </div>
            </div>
            
            <div class="puzzle-status"></div>
        `;

        // Get references to key elements
        this.wordsGrid = this.container.querySelector('.words-grid');
        this.solvedGroupsContainer = this.container.querySelector('.solved-groups-container');
        this.actionBar = this.container.querySelector('.action-bar');
    }

    /**
     * Set up event listeners
     */
    private setupEventListeners(): void {
        // Action buttons
        const shuffleBtn = this.container.querySelector('#shuffle-btn');
        const deselectBtn = this.container.querySelector('#deselect-btn');
        const recommendBtn = this.container.querySelector('#recommend-btn');
        const submitBtn = this.container.querySelector('#submit-btn');

        shuffleBtn?.addEventListener('click', () => this.shuffleWords());
        deselectBtn?.addEventListener('click', () => this.deselectAllWords());
        recommendBtn?.addEventListener('click', () => this.requestRecommendation());
        submitBtn?.addEventListener('click', () => this.submitSelectedGroup());
    }

    /**
     * Update the puzzle with new data
     */
    public updatePuzzle(puzzleData: {
        puzzleId: string;
        remainingWords: string[];
        solvedGroups: SolvedGroup[];
    }): void {
        this.puzzleState.puzzleId = puzzleData.puzzleId;
        this.puzzleState.remainingWords = [...puzzleData.remainingWords];
        this.puzzleState.solvedGroups = [...puzzleData.solvedGroups];
        this.puzzleState.selectedWords = [];

        this.renderPuzzle();
    }

    /**
     * Render the complete puzzle view
     */
    private renderPuzzle(): void {
        this.renderSolvedGroups();
        this.renderWordsGrid();
        this.updateActionBar();
    }

    /**
     * Render solved groups
     */
    private renderSolvedGroups(): void {
        if (!this.solvedGroupsContainer) return;

        this.solvedGroupsContainer.innerHTML = '';

        this.puzzleState.solvedGroups.forEach(group => {
            const groupElement = document.createElement('div');
            groupElement.className = `solved-group ${group.difficulty.toLowerCase()}`;
            groupElement.innerHTML = `
                <div class="group-theme">${group.theme}</div>
                <div class="group-words">${group.words.join(', ')}</div>
            `;
            this.solvedGroupsContainer!.appendChild(groupElement);
        });
    }

    /**
     * Render the words grid
     */
    private renderWordsGrid(): void {
        if (!this.wordsGrid) return;

        this.wordsGrid.innerHTML = '';

        const shuffledWords = [...this.puzzleState.remainingWords];
        
        shuffledWords.forEach(word => {
            const wordElement = document.createElement('div');
            wordElement.className = 'word-tile';
            wordElement.textContent = word;
            wordElement.dataset.word = word;

            // Check if word is selected
            if (this.puzzleState.selectedWords.includes(word)) {
                wordElement.classList.add('selected');
            }

            // Add click handler
            wordElement.addEventListener('click', () => this.toggleWordSelection(word));

            this.wordsGrid!.appendChild(wordElement);
        });
    }

    /**
     * Toggle word selection
     */
    private toggleWordSelection(word: string): void {
        const isCurrentlySelected = this.puzzleState.selectedWords.includes(word);
        
        if (isCurrentlySelected) {
            // Deselect word
            this.puzzleState.selectedWords = this.puzzleState.selectedWords.filter(w => w !== word);
        } else {
            // Select word (if under limit)
            if (this.puzzleState.selectedWords.length < this.puzzleState.maxSelections) {
                this.puzzleState.selectedWords.push(word);
            } else {
                this.showMessage('You can only select 4 words at a time', 'warning');
                return;
            }
        }

        // Update visual state
        const wordElement = this.wordsGrid?.querySelector(`[data-word="${word}"]`);
        if (wordElement) {
            wordElement.classList.toggle('selected', !isCurrentlySelected);
        }

        this.updateActionBar();
        this.callbacks.onWordSelected?.(word, !isCurrentlySelected);
        this.callbacks.onSelectionChanged?.(this.puzzleState.selectedWords);
    }

    /**
     * Update action bar state
     */
    private updateActionBar(): void {
        const selectionCount = this.container.querySelector('.selection-count');
        const deselectBtn = this.container.querySelector('#deselect-btn') as HTMLButtonElement;
        const submitBtn = this.container.querySelector('#submit-btn') as HTMLButtonElement;

        if (selectionCount) {
            selectionCount.textContent = this.puzzleState.selectedWords.length.toString();
        }

        if (deselectBtn) {
            deselectBtn.disabled = this.puzzleState.selectedWords.length === 0;
        }

        if (submitBtn) {
            submitBtn.disabled = this.puzzleState.selectedWords.length !== 4;
        }
    }

    /**
     * Shuffle words in the grid
     */
    private shuffleWords(): void {
        // Fisher-Yates shuffle
        const words = [...this.puzzleState.remainingWords];
        for (let i = words.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [words[i], words[j]] = [words[j]!, words[i]!];
        }
        
        this.puzzleState.remainingWords = words;
        this.renderWordsGrid();
    }

    /**
     * Deselect all words
     */
    private deselectAllWords(): void {
        this.puzzleState.selectedWords = [];
        
        // Update visual state
        const selectedElements = this.wordsGrid?.querySelectorAll('.word-tile.selected');
        selectedElements?.forEach(element => {
            element.classList.remove('selected');
        });

        this.updateActionBar();
        this.callbacks.onSelectionChanged?.(this.puzzleState.selectedWords);
    }

    /**
     * Request recommendation for current state
     */
    private requestRecommendation(): void {
        this.callbacks.onRequestRecommendation?.();
    }

    /**
     * Submit selected group
     */
    private submitSelectedGroup(): void {
        if (this.puzzleState.selectedWords.length === 4) {
            this.callbacks.onSubmitGroup?.(this.puzzleState.selectedWords);
        }
    }

    /**
     * Highlight recommended words
     */
    public highlightRecommendation(words: string[]): void {
        // Clear previous highlights
        this.clearHighlights();

        // Add recommendation highlights
        words.forEach(word => {
            const wordElement = this.wordsGrid?.querySelector(`[data-word="${word}"]`);
            if (wordElement) {
                wordElement.classList.add('recommended');
            }
        });

        // Auto-select recommended words
        this.selectWords(words);
    }

    /**
     * Clear all highlights
     */
    public clearHighlights(): void {
        const highlightedElements = this.wordsGrid?.querySelectorAll('.word-tile.recommended');
        highlightedElements?.forEach(element => {
            element.classList.remove('recommended');
        });
    }

    /**
     * Select specific words programmatically
     */
    public selectWords(words: string[]): void {
        this.deselectAllWords();
        
        words.forEach(word => {
            if (this.puzzleState.remainingWords.includes(word) && 
                this.puzzleState.selectedWords.length < this.puzzleState.maxSelections) {
                this.puzzleState.selectedWords.push(word);
                
                const wordElement = this.wordsGrid?.querySelector(`[data-word="${word}"]`);
                if (wordElement) {
                    wordElement.classList.add('selected');
                }
            }
        });

        this.updateActionBar();
        this.callbacks.onSelectionChanged?.(this.puzzleState.selectedWords);
    }

    /**
     * Add a solved group (when user gets one correct)
     */
    public addSolvedGroup(group: SolvedGroup): void {
        this.puzzleState.solvedGroups.push(group);
        
        // Remove solved words from remaining words
        this.puzzleState.remainingWords = this.puzzleState.remainingWords.filter(
            word => !group.words.includes(word)
        );
        
        // Clear selection
        this.puzzleState.selectedWords = [];
        
        this.renderPuzzle();
        this.showMessage(`Correct! "${group.theme}" group found!`, 'success');
    }

    /**
     * Handle incorrect guess
     */
    public handleIncorrectGuess(message?: string): void {
        this.showMessage(message || 'Incorrect guess. Try again!', 'error');
        
        // Briefly highlight incorrect selection
        const selectedElements = this.wordsGrid?.querySelectorAll('.word-tile.selected');
        selectedElements?.forEach(element => {
            element.classList.add('incorrect');
            setTimeout(() => {
                element.classList.remove('incorrect');
            }, 1000);
        });
    }

    /**
     * Handle one-away feedback
     */
    public handleOneAway(): void {
        this.showMessage('One away! Three of your words are in a group.', 'warning');
        
        // Brief visual feedback
        const selectedElements = this.wordsGrid?.querySelectorAll('.word-tile.selected');
        selectedElements?.forEach(element => {
            element.classList.add('one-away');
            setTimeout(() => {
                element.classList.remove('one-away');
            }, 2000);
        });
    }

    /**
     * Show status message
     */
    private showMessage(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
        const statusElement = this.container.querySelector('.puzzle-status');
        if (statusElement) {
            statusElement.className = `puzzle-status ${type}`;
            statusElement.textContent = message;
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                statusElement.textContent = '';
                statusElement.className = 'puzzle-status';
            }, 3000);
        }
    }

    /**
     * Get current selected words
     */
    public getSelectedWords(): string[] {
        return [...this.puzzleState.selectedWords];
    }

    /**
     * Get remaining words
     */
    public getRemainingWords(): string[] {
        return [...this.puzzleState.remainingWords];
    }

    /**
     * Get puzzle state
     */
    public getPuzzleState(): PuzzleState {
        return { ...this.puzzleState };
    }

    /**
     * Check if puzzle is complete
     */
    public isPuzzleComplete(): boolean {
        return this.puzzleState.solvedGroups.length === 4;
    }

    /**
     * Reset the puzzle view
     */
    public reset(): void {
        this.puzzleState = {
            puzzleId: '',
            remainingWords: [],
            solvedGroups: [],
            selectedWords: [],
            maxSelections: 4
        };
        
        this.renderPuzzle();
    }

    /**
     * Enable or disable interaction
     */
    public setEnabled(enabled: boolean): void {
        const actionButtons = this.container.querySelectorAll('.action-buttons button');
        actionButtons.forEach(button => {
            (button as HTMLButtonElement).disabled = !enabled;
        });

        if (enabled) {
            this.container.classList.remove('disabled');
        } else {
            this.container.classList.add('disabled');
        }
    }
}

// Export interfaces for use by other components
export { Word, SolvedGroup, PuzzleState, PuzzleViewCallbacks };
