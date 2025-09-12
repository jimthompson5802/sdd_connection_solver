/**
 * HistoryView component for NYT Connections Puzzle Assistant
 * 
 * Displays the history of past recommendations and evaluations
 * with filtering, sorting, and analysis capabilities.
 */

// History item interface
interface HistoryItem {
    id: string;
    timestamp: Date;
    recommendedWords: string[];
    explanation: string;
    userEvaluation?: 'correct' | 'incorrect' | 'one_away';
    evaluationTimestamp?: Date;
    llmModel: string;
    processingTimeMs: number;
    sessionId: string;
}

// History view configuration
interface HistoryViewConfig {
    itemsPerPage: number;
    showTimestamps: boolean;
    showProcessingTimes: boolean;
    enableFiltering: boolean;
    enableSorting: boolean;
    compactMode: boolean;
}

// History view callbacks
interface HistoryViewCallbacks {
    onItemSelected?: (item: HistoryItem) => void;
    onWordsHighlight?: (words: string[]) => void;
    onClearHighlight?: () => void;
    onExportHistory?: (items: HistoryItem[]) => void;
}

// Filter options
interface HistoryFilter {
    evaluation?: 'all' | 'correct' | 'incorrect' | 'one_away' | 'unevaluated';
    timeRange?: 'all' | 'last_hour' | 'last_session' | 'today';
    model?: 'all' | string;
}

// Sort options
type SortOption = 'timestamp_desc' | 'timestamp_asc' | 'evaluation' | 'processing_time';

/**
 * HistoryView component class for displaying recommendation history
 */
export class HistoryView {
    private container: HTMLElement;
    private historyItems: HistoryItem[] = [];
    private filteredItems: HistoryItem[] = [];
    private config: HistoryViewConfig;
    private callbacks: HistoryViewCallbacks;
    private currentFilter: HistoryFilter = { evaluation: 'all', timeRange: 'all', model: 'all' };
    private currentSort: SortOption = 'timestamp_desc';
    private currentPage = 1;

    constructor(
        containerId: string, 
        config?: Partial<HistoryViewConfig>, 
        callbacks?: HistoryViewCallbacks
    ) {
        this.container = document.getElementById(containerId) || document.body;
        this.config = {
            itemsPerPage: 10,
            showTimestamps: true,
            showProcessingTimes: true,
            enableFiltering: true,
            enableSorting: true,
            compactMode: false,
            ...config
        };
        this.callbacks = callbacks || {};
        
        this.createElements();
        this.setupEventListeners();
    }

    /**
     * Create the DOM elements for the history view
     */
    private createElements(): void {
        this.container.className = 'history-view-container';
        this.container.innerHTML = `
            <div class="history-header">
                <h3 class="history-title">Recommendation History</h3>
                <div class="history-controls">
                    ${this.config.enableFiltering ? this.createFiltersHTML() : ''}
                    ${this.config.enableSorting ? this.createSortingHTML() : ''}
                    <div class="history-actions">
                        <button class="btn btn-outline btn-sm" id="export-history-btn">Export</button>
                        <button class="btn btn-outline btn-sm" id="clear-history-btn">Clear</button>
                        <button class="btn btn-outline btn-sm" id="toggle-compact-btn">
                            ${this.config.compactMode ? 'Expand' : 'Compact'}
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="history-stats">
                <div class="stats-item">
                    <span class="stats-value" id="total-count">0</span>
                    <span class="stats-label">Total</span>
                </div>
                <div class="stats-item">
                    <span class="stats-value" id="correct-count">0</span>
                    <span class="stats-label">Correct</span>
                </div>
                <div class="stats-item">
                    <span class="stats-value" id="incorrect-count">0</span>
                    <span class="stats-label">Incorrect</span>
                </div>
                <div class="stats-item">
                    <span class="stats-value" id="one-away-count">0</span>
                    <span class="stats-label">One Away</span>
                </div>
                <div class="stats-item">
                    <span class="stats-value" id="success-rate">0%</span>
                    <span class="stats-label">Success Rate</span>
                </div>
            </div>
            
            <div class="history-content">
                <div class="history-list"></div>
                <div class="history-pagination"></div>
            </div>
            
            <div class="history-empty" style="display: none;">
                <div class="empty-icon">📝</div>
                <div class="empty-text">
                    <p>No recommendations yet</p>
                    <p class="empty-subtitle">Your AI recommendation history will appear here</p>
                </div>
            </div>
        `;
    }

    /**
     * Create filters HTML
     */
    private createFiltersHTML(): string {
        return `
            <div class="history-filters">
                <select id="evaluation-filter" class="filter-select">
                    <option value="all">All Evaluations</option>
                    <option value="correct">Correct</option>
                    <option value="incorrect">Incorrect</option>
                    <option value="one_away">One Away</option>
                    <option value="unevaluated">Unevaluated</option>
                </select>
                <select id="time-filter" class="filter-select">
                    <option value="all">All Time</option>
                    <option value="today">Today</option>
                    <option value="last_session">Last Session</option>
                    <option value="last_hour">Last Hour</option>
                </select>
                <select id="model-filter" class="filter-select">
                    <option value="all">All Models</option>
                </select>
            </div>
        `;
    }

    /**
     * Create sorting HTML
     */
    private createSortingHTML(): string {
        return `
            <div class="history-sorting">
                <select id="sort-select" class="sort-select">
                    <option value="timestamp_desc">Newest First</option>
                    <option value="timestamp_asc">Oldest First</option>
                    <option value="evaluation">By Evaluation</option>
                    <option value="processing_time">By Processing Time</option>
                </select>
            </div>
        `;
    }

    /**
     * Set up event listeners
     */
    private setupEventListeners(): void {
        // Filter controls
        const evaluationFilter = this.container.querySelector('#evaluation-filter');
        const timeFilter = this.container.querySelector('#time-filter');
        const modelFilter = this.container.querySelector('#model-filter');
        const sortSelect = this.container.querySelector('#sort-select');

        evaluationFilter?.addEventListener('change', (e) => {
            this.currentFilter.evaluation = (e.target as HTMLSelectElement).value as any;
            this.applyFiltersAndSort();
        });

        timeFilter?.addEventListener('change', (e) => {
            this.currentFilter.timeRange = (e.target as HTMLSelectElement).value as any;
            this.applyFiltersAndSort();
        });

        modelFilter?.addEventListener('change', (e) => {
            this.currentFilter.model = (e.target as HTMLSelectElement).value;
            this.applyFiltersAndSort();
        });

        sortSelect?.addEventListener('change', (e) => {
            this.currentSort = (e.target as HTMLSelectElement).value as SortOption;
            this.applyFiltersAndSort();
        });

        // Action buttons
        const exportBtn = this.container.querySelector('#export-history-btn');
        const clearBtn = this.container.querySelector('#clear-history-btn');
        const toggleCompactBtn = this.container.querySelector('#toggle-compact-btn');

        exportBtn?.addEventListener('click', () => this.exportHistory());
        clearBtn?.addEventListener('click', () => this.clearHistory());
        toggleCompactBtn?.addEventListener('click', () => this.toggleCompactMode());
    }

    /**
     * Add a new history item
     */
    public addHistoryItem(item: HistoryItem): void {
        this.historyItems.unshift(item); // Add to beginning (newest first)
        this.updateModelFilter();
        this.applyFiltersAndSort();
        this.updateStats();
    }

    /**
     * Update an existing history item
     */
    public updateHistoryItem(itemId: string, updates: Partial<HistoryItem>): void {
        const index = this.historyItems.findIndex(item => item.id === itemId);
        if (index !== -1) {
            this.historyItems[index] = Object.assign({}, this.historyItems[index], updates);
            this.applyFiltersAndSort();
            this.updateStats();
        }
    }

    /**
     * Set the complete history
     */
    public setHistory(items: HistoryItem[]): void {
        this.historyItems = [...items];
        this.updateModelFilter();
        this.applyFiltersAndSort();
        this.updateStats();
    }

    /**
     * Apply current filters and sorting
     */
    private applyFiltersAndSort(): void {
        // Apply filters
        this.filteredItems = this.historyItems.filter(item => this.matchesFilter(item));
        
        // Apply sorting
        this.filteredItems.sort((a, b) => this.compareItems(a, b));
        
        // Reset to first page
        this.currentPage = 1;
        
        // Render results
        this.renderHistoryList();
        this.renderPagination();
    }

    /**
     * Check if item matches current filter
     */
    private matchesFilter(item: HistoryItem): boolean {
        // Evaluation filter
        if (this.currentFilter.evaluation !== 'all') {
            if (this.currentFilter.evaluation === 'unevaluated') {
                if (item.userEvaluation) return false;
            } else {
                if (item.userEvaluation !== this.currentFilter.evaluation) return false;
            }
        }

        // Time range filter
        if (this.currentFilter.timeRange !== 'all') {
            const now = new Date();
            const itemTime = item.timestamp;
            
            switch (this.currentFilter.timeRange) {
                case 'last_hour':
                    if (now.getTime() - itemTime.getTime() > 60 * 60 * 1000) return false;
                    break;
                case 'today':
                    if (itemTime.toDateString() !== now.toDateString()) return false;
                    break;
                case 'last_session':
                    // Would need session data to implement properly
                    break;
            }
        }

        // Model filter
        if (this.currentFilter.model !== 'all' && item.llmModel !== this.currentFilter.model) {
            return false;
        }

        return true;
    }

    /**
     * Compare items for sorting
     */
    private compareItems(a: HistoryItem, b: HistoryItem): number {
        switch (this.currentSort) {
            case 'timestamp_desc':
                return b.timestamp.getTime() - a.timestamp.getTime();
            case 'timestamp_asc':
                return a.timestamp.getTime() - b.timestamp.getTime();
            case 'evaluation':
                const evalOrder = { 'correct': 1, 'one_away': 2, 'incorrect': 3 };
                const aEval = a.userEvaluation ? evalOrder[a.userEvaluation as keyof typeof evalOrder] : 4;
                const bEval = b.userEvaluation ? evalOrder[b.userEvaluation as keyof typeof evalOrder] : 4;
                return aEval - bEval;
            case 'processing_time':
                return a.processingTimeMs - b.processingTimeMs;
            default:
                return 0;
        }
    }

    /**
     * Render the history list
     */
    private renderHistoryList(): void {
        const historyList = this.container.querySelector('.history-list');
        const historyEmpty = this.container.querySelector('.history-empty') as HTMLElement;
        
        if (!historyList) return;

        if (this.filteredItems.length === 0) {
            historyList.innerHTML = '';
            historyEmpty.style.display = 'block';
            return;
        }

        historyEmpty.style.display = 'none';

        // Calculate pagination
        const startIndex = (this.currentPage - 1) * this.config.itemsPerPage;
        const endIndex = startIndex + this.config.itemsPerPage;
        const pageItems = this.filteredItems.slice(startIndex, endIndex);

        // Render items
        historyList.innerHTML = pageItems.map(item => this.renderHistoryItem(item)).join('');
        
        // Add event listeners to items
        this.setupItemEventListeners();
    }

    /**
     * Render a single history item
     */
    private renderHistoryItem(item: HistoryItem): string {
        const evaluationClass = item.userEvaluation || 'unevaluated';
        const evaluationIcon = this.getEvaluationIcon(item.userEvaluation);
        const evaluationText = this.getEvaluationText(item.userEvaluation);

        return `
            <div class="history-item ${evaluationClass} ${this.config.compactMode ? 'compact' : ''}" 
                 data-item-id="${item.id}">
                <div class="item-header">
                    <div class="item-evaluation">
                        <span class="evaluation-icon">${evaluationIcon}</span>
                        <span class="evaluation-text">${evaluationText}</span>
                    </div>
                    ${this.config.showTimestamps ? `
                        <div class="item-timestamp">
                            ${this.formatTimestamp(item.timestamp)}
                        </div>
                    ` : ''}
                </div>
                
                <div class="item-content">
                    <div class="recommended-words">
                        ${item.recommendedWords.map(word => 
                            `<span class="word-chip" data-word="${word}">${word}</span>`
                        ).join('')}
                    </div>
                    
                    ${!this.config.compactMode ? `
                        <div class="item-explanation">
                            ${item.explanation}
                        </div>
                    ` : ''}
                </div>
                
                <div class="item-footer">
                    <div class="item-meta">
                        <span class="item-model">${item.llmModel}</span>
                        ${this.config.showProcessingTimes ? `
                            <span class="item-processing-time">${item.processingTimeMs}ms</span>
                        ` : ''}
                    </div>
                    <div class="item-actions">
                        <button class="btn btn-sm btn-outline highlight-words-btn">Highlight</button>
                        ${!this.config.compactMode ? `
                            <button class="btn btn-sm btn-outline view-details-btn">Details</button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Set up event listeners for history items
     */
    private setupItemEventListeners(): void {
        // Word chip highlights
        this.container.querySelectorAll('.word-chip').forEach(chip => {
            chip.addEventListener('mouseenter', () => {
                const words = this.getItemWords(chip.closest('.history-item')!);
                this.callbacks.onWordsHighlight?.(words);
            });
            
            chip.addEventListener('mouseleave', () => {
                this.callbacks.onClearHighlight?.();
            });
        });

        // Highlight buttons
        this.container.querySelectorAll('.highlight-words-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = (e.target as HTMLElement).closest('.history-item')!;
                const words = this.getItemWords(item);
                this.callbacks.onWordsHighlight?.(words);
            });
        });

        // View details buttons
        this.container.querySelectorAll('.view-details-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = (e.target as HTMLElement).closest('.history-item')!;
                const itemId = item.getAttribute('data-item-id')!;
                const historyItem = this.historyItems.find(h => h.id === itemId);
                if (historyItem) {
                    this.callbacks.onItemSelected?.(historyItem);
                }
            });
        });

        // Item click (for selection)
        this.container.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => {
                // Remove previous selection
                this.container.querySelectorAll('.history-item.selected').forEach(el => {
                    el.classList.remove('selected');
                });
                
                // Add selection to clicked item
                item.classList.add('selected');
            });
        });
    }

    /**
     * Get words from a history item element
     */
    private getItemWords(itemElement: Element): string[] {
        const wordChips = itemElement.querySelectorAll('.word-chip');
        return Array.from(wordChips).map(chip => chip.getAttribute('data-word')!);
    }

    /**
     * Render pagination controls
     */
    private renderPagination(): void {
        const paginationContainer = this.container.querySelector('.history-pagination');
        if (!paginationContainer) return;

        const totalPages = Math.ceil(this.filteredItems.length / this.config.itemsPerPage);
        
        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }

        const pages = [];
        for (let i = 1; i <= totalPages; i++) {
            pages.push(`
                <button class="pagination-btn ${i === this.currentPage ? 'active' : ''}" 
                        data-page="${i}">${i}</button>
            `);
        }

        paginationContainer.innerHTML = `
            <div class="pagination">
                <button class="pagination-btn" data-page="prev" ${this.currentPage === 1 ? 'disabled' : ''}>
                    ‹ Prev
                </button>
                ${pages.join('')}
                <button class="pagination-btn" data-page="next" ${this.currentPage === totalPages ? 'disabled' : ''}>
                    Next ›
                </button>
            </div>
        `;

        // Add pagination event listeners
        paginationContainer.querySelectorAll('.pagination-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = (e.target as HTMLElement).getAttribute('data-page');
                if (page === 'prev' && this.currentPage > 1) {
                    this.currentPage--;
                } else if (page === 'next' && this.currentPage < totalPages) {
                    this.currentPage++;
                } else if (page && !isNaN(parseInt(page))) {
                    this.currentPage = parseInt(page);
                }
                this.renderHistoryList();
                this.renderPagination();
            });
        });
    }

    /**
     * Update statistics display
     */
    private updateStats(): void {
        const total = this.historyItems.length;
        const correct = this.historyItems.filter(item => item.userEvaluation === 'correct').length;
        const incorrect = this.historyItems.filter(item => item.userEvaluation === 'incorrect').length;
        const oneAway = this.historyItems.filter(item => item.userEvaluation === 'one_away').length;
        const evaluated = correct + incorrect + oneAway;
        const successRate = evaluated > 0 ? Math.round((correct / evaluated) * 100) : 0;

        this.updateStatValue('total-count', total.toString());
        this.updateStatValue('correct-count', correct.toString());
        this.updateStatValue('incorrect-count', incorrect.toString());
        this.updateStatValue('one-away-count', oneAway.toString());
        this.updateStatValue('success-rate', `${successRate}%`);
    }

    /**
     * Update a stat value
     */
    private updateStatValue(elementId: string, value: string): void {
        const element = this.container.querySelector(`#${elementId}`);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Update model filter options
     */
    private updateModelFilter(): void {
        const modelFilter = this.container.querySelector('#model-filter') as HTMLSelectElement;
        if (!modelFilter) return;

        const models = [...new Set(this.historyItems.map(item => item.llmModel))];
        const currentValue = modelFilter.value;

        modelFilter.innerHTML = '<option value="all">All Models</option>';
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            modelFilter.appendChild(option);
        });

        modelFilter.value = currentValue;
    }

    /**
     * Get evaluation icon
     */
    private getEvaluationIcon(evaluation?: string): string {
        const icons = {
            correct: '✅',
            incorrect: '❌',
            one_away: '⚠️'
        };
        return icons[evaluation as keyof typeof icons] || '⏳';
    }

    /**
     * Get evaluation text
     */
    private getEvaluationText(evaluation?: string): string {
        const texts = {
            correct: 'Correct',
            incorrect: 'Incorrect',
            one_away: 'One Away'
        };
        return texts[evaluation as keyof typeof texts] || 'Pending';
    }

    /**
     * Format timestamp
     */
    private formatTimestamp(timestamp: Date): string {
        const now = new Date();
        const diff = now.getTime() - timestamp.getTime();
        const minutes = Math.floor(diff / (1000 * 60));
        
        if (minutes < 1) {
            return 'just now';
        } else if (minutes < 60) {
            return `${minutes}m ago`;
        } else {
            return timestamp.toLocaleTimeString();
        }
    }

    /**
     * Export history
     */
    private exportHistory(): void {
        this.callbacks.onExportHistory?.(this.filteredItems);
    }

    /**
     * Clear history with confirmation
     */
    private clearHistory(): void {
        if (confirm('Are you sure you want to clear all history? This cannot be undone.')) {
            this.historyItems = [];
            this.filteredItems = [];
            this.applyFiltersAndSort();
            this.updateStats();
        }
    }

    /**
     * Toggle compact mode
     */
    private toggleCompactMode(): void {
        this.config.compactMode = !this.config.compactMode;
        const toggleBtn = this.container.querySelector('#toggle-compact-btn');
        if (toggleBtn) {
            toggleBtn.textContent = this.config.compactMode ? 'Expand' : 'Compact';
        }
        this.renderHistoryList();
    }

    /**
     * Get all history items
     */
    public getHistory(): HistoryItem[] {
        return [...this.historyItems];
    }

    /**
     * Get filtered history items
     */
    public getFilteredHistory(): HistoryItem[] {
        return [...this.filteredItems];
    }

    /**
     * Clear all history
     */
    public clear(): void {
        this.historyItems = [];
        this.filteredItems = [];
        this.currentPage = 1;
        this.applyFiltersAndSort();
        this.updateStats();
    }

    /**
     * Check if history is empty
     */
    public isEmpty(): boolean {
        return this.historyItems.length === 0;
    }
}

// Export interfaces for use by other components
export { 
    HistoryItem, 
    HistoryViewConfig, 
    HistoryViewCallbacks, 
    HistoryFilter, 
    SortOption 
};
