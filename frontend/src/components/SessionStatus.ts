/**
 * SessionStatus component for NYT Connections Puzzle Assistant
 * 
 * Displays current session progress including solved groups count,
 * remaining attempts, session time, and overall game status.
 */

// Session status data interface
interface SessionStatusData {
    sessionId: string;
    puzzleId: string;
    status: 'active' | 'completed' | 'failed' | 'abandoned';
    startTime: Date;
    lastActivity: Date;
    solvedGroupsCount: number;
    incorrectEvaluationCount: number;
    totalRecommendations: number;
    remainingWords: number;
    maxIncorrectAttempts: number;
    llmModel: string;
}

// Session statistics interface
interface SessionStats {
    elapsedTime: string;
    averageRecommendationTime: number;
    successRate: number;
    groupsRemaining: number;
    attemptsRemaining: number;
}

// Session status callbacks
interface SessionStatusCallbacks {
    onSessionEnd?: (reason: 'completed' | 'failed' | 'abandoned') => void;
    onWarning?: (message: string) => void;
    onAchievement?: (achievement: string) => void;
}

/**
 * SessionStatus component class for displaying game progress and statistics
 */
export class SessionStatus {
    private container: HTMLElement;
    private sessionStatus: SessionStatusData | null = null;
    private callbacks: SessionStatusCallbacks;
    private updateInterval: number | null = null;

    constructor(containerId: string, callbacks?: SessionStatusCallbacks) {
        this.container = document.getElementById(containerId) || document.body;
        this.callbacks = callbacks || {};
        
        this.createElements();
        this.startPeriodicUpdates();
    }

    /**
     * Create the DOM elements for the session status
     */
    private createElements(): void {
        this.container.className = 'session-status-container';
        this.container.innerHTML = `
            <div class="session-status-card">
                <div class="status-header">
                    <h3 class="status-title">Session Progress</h3>
                    <div class="session-id"></div>
                </div>
                
                <div class="progress-overview">
                    <div class="progress-grid">
                        <div class="progress-item groups-solved">
                            <div class="progress-icon">🎯</div>
                            <div class="progress-content">
                                <div class="progress-value">0/4</div>
                                <div class="progress-label">Groups Found</div>
                            </div>
                        </div>
                        
                        <div class="progress-item attempts-remaining">
                            <div class="progress-icon">💪</div>
                            <div class="progress-content">
                                <div class="progress-value">4</div>
                                <div class="progress-label">Attempts Left</div>
                            </div>
                        </div>
                        
                        <div class="progress-item elapsed-time">
                            <div class="progress-icon">⏱️</div>
                            <div class="progress-content">
                                <div class="progress-value">00:00</div>
                                <div class="progress-label">Time Elapsed</div>
                            </div>
                        </div>
                        
                        <div class="progress-item success-rate">
                            <div class="progress-icon">📊</div>
                            <div class="progress-content">
                                <div class="progress-value">--%</div>
                                <div class="progress-label">Success Rate</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="progress-bars">
                    <div class="progress-bar-item">
                        <div class="progress-bar-label">
                            <span>Groups Progress</span>
                            <span class="progress-percentage">0%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill groups-progress"></div>
                        </div>
                    </div>
                    
                    <div class="progress-bar-item">
                        <div class="progress-bar-label">
                            <span>Attempts Used</span>
                            <span class="attempts-percentage">0%</span>
                        </div>
                        <div class="progress-bar danger">
                            <div class="progress-fill attempts-progress"></div>
                        </div>
                    </div>
                </div>
                
                <div class="session-details">
                    <div class="details-grid">
                        <div class="detail-item">
                            <span class="detail-label">Status:</span>
                            <span class="detail-value session-status-value">Not Started</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">AI Model:</span>
                            <span class="detail-value ai-model">-</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Words Left:</span>
                            <span class="detail-value words-remaining">16</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Recommendations:</span>
                            <span class="detail-value total-recommendations">0</span>
                        </div>
                    </div>
                </div>
                
                <div class="session-actions">
                    <button class="btn btn-outline btn-sm" id="session-stats-btn">View Stats</button>
                    <button class="btn btn-outline btn-sm" id="session-reset-btn">Reset Session</button>
                </div>
                
                <div class="status-messages"></div>
            </div>
        `;

        this.setupEventListeners();
    }

    /**
     * Set up event listeners
     */
    private setupEventListeners(): void {
        const statsBtn = this.container.querySelector('#session-stats-btn');
        const resetBtn = this.container.querySelector('#session-reset-btn');

        statsBtn?.addEventListener('click', () => this.showDetailedStats());
        resetBtn?.addEventListener('click', () => this.resetSession());
    }

    /**
     * Update session status with new data
     */
    public updateSession(status: SessionStatusData): void {
        this.sessionStatus = status;
        this.renderStatus();
        this.checkForWarnings();
        this.checkForAchievements();
    }

    /**
     * Render the complete status display
     */
    private renderStatus(): void {
        if (!this.sessionStatus) return;

        this.updateProgressItems();
        this.updateProgressBars();
        this.updateSessionDetails();
        this.updateSessionId();
    }

    /**
     * Update progress items in the grid
     */
    private updateProgressItems(): void {
        if (!this.sessionStatus) return;

        const stats = this.calculateStats();

        // Groups solved
        const groupsValue = this.container.querySelector('.groups-solved .progress-value');
        if (groupsValue) {
            groupsValue.textContent = `${this.sessionStatus.solvedGroupsCount}/4`;
        }

        // Attempts remaining
        const attemptsValue = this.container.querySelector('.attempts-remaining .progress-value');
        if (attemptsValue) {
            const remaining = this.sessionStatus.maxIncorrectAttempts - this.sessionStatus.incorrectEvaluationCount;
            attemptsValue.textContent = remaining.toString();
        }

        // Elapsed time
        const timeValue = this.container.querySelector('.elapsed-time .progress-value');
        if (timeValue) {
            timeValue.textContent = stats.elapsedTime;
        }

        // Success rate
        const successValue = this.container.querySelector('.success-rate .progress-value');
        if (successValue) {
            successValue.textContent = `${Math.round(stats.successRate)}%`;
        }
    }

    /**
     * Update progress bars
     */
    private updateProgressBars(): void {
        if (!this.sessionStatus) return;

        // Groups progress
        const groupsProgress = (this.sessionStatus.solvedGroupsCount / 4) * 100;
        const groupsProgressElement = this.container.querySelector('.groups-progress') as HTMLElement;
        const groupsPercentageElement = this.container.querySelector('.progress-percentage');
        
        if (groupsProgressElement) {
            groupsProgressElement.style.width = `${groupsProgress}%`;
        }
        if (groupsPercentageElement) {
            groupsPercentageElement.textContent = `${Math.round(groupsProgress)}%`;
        }

        // Attempts progress
        const attemptsProgress = (this.sessionStatus.incorrectEvaluationCount / this.sessionStatus.maxIncorrectAttempts) * 100;
        const attemptsProgressElement = this.container.querySelector('.attempts-progress') as HTMLElement;
        const attemptsPercentageElement = this.container.querySelector('.attempts-percentage');
        
        if (attemptsProgressElement) {
            attemptsProgressElement.style.width = `${attemptsProgress}%`;
        }
        if (attemptsPercentageElement) {
            attemptsPercentageElement.textContent = `${Math.round(attemptsProgress)}%`;
        }
    }

    /**
     * Update session details
     */
    private updateSessionDetails(): void {
        if (!this.sessionStatus) return;

        // Session status
        const statusValue = this.container.querySelector('.session-status-value');
        if (statusValue) {
            statusValue.textContent = this.formatSessionStatus(this.sessionStatus.status);
            statusValue.className = `detail-value session-status-value ${this.sessionStatus.status}`;
        }

        // AI Model
        const aiModel = this.container.querySelector('.ai-model');
        if (aiModel) {
            aiModel.textContent = this.sessionStatus.llmModel;
        }

        // Words remaining
        const wordsRemaining = this.container.querySelector('.words-remaining');
        if (wordsRemaining) {
            wordsRemaining.textContent = this.sessionStatus.remainingWords.toString();
        }

        // Total recommendations
        const totalRecommendations = this.container.querySelector('.total-recommendations');
        if (totalRecommendations) {
            totalRecommendations.textContent = this.sessionStatus.totalRecommendations.toString();
        }
    }

    /**
     * Update session ID display
     */
    private updateSessionId(): void {
        if (!this.sessionStatus) return;

        const sessionIdElement = this.container.querySelector('.session-id');
        if (sessionIdElement) {
            sessionIdElement.textContent = `Session: ${this.sessionStatus.sessionId.substring(0, 8)}...`;
        }
    }

    /**
     * Calculate session statistics
     */
    private calculateStats(): SessionStats {
        if (!this.sessionStatus) {
            return {
                elapsedTime: '00:00',
                averageRecommendationTime: 0,
                successRate: 0,
                groupsRemaining: 4,
                attemptsRemaining: 4
            };
        }

        const now = new Date();
        const elapsed = now.getTime() - this.sessionStatus.startTime.getTime();
        const minutes = Math.floor(elapsed / (1000 * 60));
        const seconds = Math.floor((elapsed % (1000 * 60)) / 1000);
        const elapsedTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        const successRate = this.sessionStatus.totalRecommendations > 0 ?
            (this.sessionStatus.solvedGroupsCount / this.sessionStatus.totalRecommendations) * 100 : 0;

        return {
            elapsedTime,
            averageRecommendationTime: 0, // Would need more data to calculate
            successRate,
            groupsRemaining: 4 - this.sessionStatus.solvedGroupsCount,
            attemptsRemaining: this.sessionStatus.maxIncorrectAttempts - this.sessionStatus.incorrectEvaluationCount
        };
    }

    /**
     * Format session status for display
     */
    private formatSessionStatus(status: string): string {
        const statusMap = {
            active: 'In Progress',
            completed: 'Completed ✅',
            failed: 'Failed ❌',
            abandoned: 'Abandoned'
        };
        return statusMap[status as keyof typeof statusMap] || status;
    }

    /**
     * Check for warnings and notify
     */
    private checkForWarnings(): void {
        if (!this.sessionStatus) return;

        const attemptsRemaining = this.sessionStatus.maxIncorrectAttempts - this.sessionStatus.incorrectEvaluationCount;
        
        if (attemptsRemaining === 1) {
            this.showMessage('⚠️ Last attempt remaining!', 'warning');
            this.callbacks.onWarning?.('Only one incorrect attempt remaining');
        } else if (attemptsRemaining === 0 && this.sessionStatus.status === 'active') {
            this.showMessage('❌ No attempts remaining - Session failed', 'error');
            this.callbacks.onSessionEnd?.('failed');
        }

        if (this.sessionStatus.solvedGroupsCount === 4 && this.sessionStatus.status === 'active') {
            this.showMessage('🎉 Puzzle completed successfully!', 'success');
            this.callbacks.onSessionEnd?.('completed');
        }
    }

    /**
     * Check for achievements and notify
     */
    private checkForAchievements(): void {
        if (!this.sessionStatus) return;

        // Perfect game (all groups found without errors)
        if (this.sessionStatus.solvedGroupsCount === 4 && this.sessionStatus.incorrectEvaluationCount === 0) {
            this.callbacks.onAchievement?.('Perfect Game! All groups found without mistakes.');
        }

        // Fast completion (under 5 minutes)
        const elapsed = new Date().getTime() - this.sessionStatus.startTime.getTime();
        if (this.sessionStatus.solvedGroupsCount === 4 && elapsed < 5 * 60 * 1000) {
            this.callbacks.onAchievement?.('Speed Demon! Completed in under 5 minutes.');
        }

        // High efficiency (few recommendations needed)
        if (this.sessionStatus.solvedGroupsCount === 4 && this.sessionStatus.totalRecommendations <= 5) {
            this.callbacks.onAchievement?.('Efficient Solver! Completed with minimal AI help.');
        }
    }

    /**
     * Show detailed statistics modal
     */
    private showDetailedStats(): void {
        if (!this.sessionStatus) return;

        const stats = this.calculateStats();
        
        // Create modal content
        const modalContent = `
            <div class="stats-modal">
                <h4>Detailed Session Statistics</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Session Duration:</span>
                        <span class="stat-value">${stats.elapsedTime}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Groups Found:</span>
                        <span class="stat-value">${this.sessionStatus.solvedGroupsCount}/4</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Success Rate:</span>
                        <span class="stat-value">${Math.round(stats.successRate)}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Incorrect Attempts:</span>
                        <span class="stat-value">${this.sessionStatus.incorrectEvaluationCount}/${this.sessionStatus.maxIncorrectAttempts}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Total Recommendations:</span>
                        <span class="stat-value">${this.sessionStatus.totalRecommendations}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">AI Model Used:</span>
                        <span class="stat-value">${this.sessionStatus.llmModel}</span>
                    </div>
                </div>
                <button class="btn btn-primary close-stats">Close</button>
            </div>
        `;

        // Show in a simple overlay (in a real app, might use a proper modal)
        const overlay = document.createElement('div');
        overlay.className = 'stats-overlay';
        overlay.innerHTML = modalContent;
        document.body.appendChild(overlay);

        // Close button handler
        overlay.querySelector('.close-stats')?.addEventListener('click', () => {
            document.body.removeChild(overlay);
        });

        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                document.body.removeChild(overlay);
            }
        });
    }

    /**
     * Reset session (with confirmation)
     */
    private resetSession(): void {
        if (confirm('Are you sure you want to reset the current session? This will lose all progress.')) {
            this.sessionStatus = null;
            this.createElements();
            this.callbacks.onSessionEnd?.('abandoned');
        }
    }

    /**
     * Show status message
     */
    private showMessage(message: string, type: 'info' | 'warning' | 'error' | 'success' = 'info'): void {
        const messagesContainer = this.container.querySelector('.status-messages');
        if (messagesContainer) {
            const messageElement = document.createElement('div');
            messageElement.className = `status-message ${type}`;
            messageElement.textContent = message;
            
            messagesContainer.appendChild(messageElement);

            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.parentNode.removeChild(messageElement);
                }
            }, 5000);
        }
    }

    /**
     * Start periodic updates for time elapsed
     */
    private startPeriodicUpdates(): void {
        this.updateInterval = window.setInterval(() => {
            if (this.sessionStatus && this.sessionStatus.status === 'active') {
                this.updateProgressItems(); // Update elapsed time
            }
        }, 1000); // Update every second
    }

    /**
     * Stop periodic updates
     */
    private stopPeriodicUpdates(): void {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * Get current session statistics
     */
    public getStats(): SessionStats | null {
        return this.sessionStatus ? this.calculateStats() : null;
    }

    /**
     * Check if session is active
     */
    public isSessionActive(): boolean {
        return this.sessionStatus?.status === 'active';
    }

    /**
     * Get current session status
     */
    public getCurrentSession(): SessionStatusData | null {
        return this.sessionStatus;
    }

    /**
     * Clear session data
     */
    public clear(): void {
        this.sessionStatus = null;
        this.createElements();
    }

    /**
     * Destroy component and clean up
     */
    public destroy(): void {
        this.stopPeriodicUpdates();
        this.container.innerHTML = '';
    }
}

// Export interfaces for use by other components
export { SessionStatusData, SessionStats, SessionStatusCallbacks };
