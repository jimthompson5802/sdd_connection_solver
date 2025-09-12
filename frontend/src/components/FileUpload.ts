/**
 * FileUpload component for NYT Connections Puzzle Assistant
 * 
 * Provides drag-and-drop file upload functionality for puzzle text files.
 * Supports CSV and TXT formats with 16 words as required by the puzzle.
 */

// File upload configuration
interface FileUploadConfig {
    maxFileSize: number; // in bytes
    allowedFileTypes: string[];
    maxWords: number;
    minWords: number;
}

// File upload result interface
interface FileUploadResult {
    success: boolean;
    filename: string;
    words: string[];
    error?: string;
}

// File upload event callbacks
interface FileUploadCallbacks {
    onFileSelected?: (file: File) => void;
    onFileUploaded?: (result: FileUploadResult) => void;
    onError?: (error: string) => void;
    onProgress?: (progress: number) => void;
}

/**
 * FileUpload component class for handling file upload operations
 */
export class FileUpload {
    private container: HTMLElement;
    private dropZone!: HTMLElement;
    private fileInput!: HTMLInputElement;
    private progressBar!: HTMLElement;
    private statusMessage!: HTMLElement;
    private config: FileUploadConfig;
    private callbacks: FileUploadCallbacks;

    constructor(containerId: string, config?: Partial<FileUploadConfig>, callbacks?: FileUploadCallbacks) {
        this.container = document.getElementById(containerId) || document.body;
        this.config = {
            maxFileSize: 1024 * 1024, // 1MB
            allowedFileTypes: ['text/plain', 'text/csv', 'application/csv'],
            maxWords: 16,
            minWords: 16,
            ...config
        };
        this.callbacks = callbacks || {};
        
        this.createElements();
        this.setupEventListeners();
    }

    /**
     * Create the DOM elements for the file upload component
     */
    private createElements(): void {
        // Main drop zone
        this.dropZone = document.createElement('div');
        this.dropZone.className = 'file-upload-drop-zone';
        this.dropZone.innerHTML = `
            <div class="drop-zone-content">
                <div class="drop-zone-icon">📁</div>
                <div class="drop-zone-text">
                    <p>Drag and drop your puzzle file here</p>
                    <p class="drop-zone-subtitle">or <span class="file-browse-link">browse files</span></p>
                    <p class="file-requirements">Supported: TXT, CSV (exactly 16 words)</p>
                </div>
            </div>
        `;

        // Hidden file input
        this.fileInput = document.createElement('input');
        this.fileInput.type = 'file';
        this.fileInput.accept = '.txt,.csv';
        this.fileInput.style.display = 'none';

        // Progress bar
        this.progressBar = document.createElement('div');
        this.progressBar.className = 'file-upload-progress';
        this.progressBar.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <div class="progress-text">0%</div>
        `;
        this.progressBar.style.display = 'none';

        // Status message
        this.statusMessage = document.createElement('div');
        this.statusMessage.className = 'file-upload-status';

        // Append elements to container
        this.container.appendChild(this.dropZone);
        this.container.appendChild(this.fileInput);
        this.container.appendChild(this.progressBar);
        this.container.appendChild(this.statusMessage);

        // Add CSS classes to container
        this.container.classList.add('file-upload-container');
    }

    /**
     * Set up event listeners for drag-and-drop and file selection
     */
    private setupEventListeners(): void {
        // Drag and drop events
        this.dropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        this.dropZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.dropZone.addEventListener('drop', this.handleDrop.bind(this));

        // Click to browse files
        const browseLink = this.dropZone.querySelector('.file-browse-link');
        if (browseLink) {
            browseLink.addEventListener('click', () => {
                this.fileInput.click();
            });
        }

        // File input change
        this.fileInput.addEventListener('change', this.handleFileInputChange.bind(this));

        // Prevent default drag behaviors on the document
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => e.preventDefault());
    }

    /**
     * Handle drag over event
     */
    private handleDragOver(event: DragEvent): void {
        event.preventDefault();
        this.dropZone.classList.add('drag-over');
    }

    /**
     * Handle drag leave event
     */
    private handleDragLeave(event: DragEvent): void {
        event.preventDefault();
        this.dropZone.classList.remove('drag-over');
    }

    /**
     * Handle drop event
     */
    private handleDrop(event: DragEvent): void {
        event.preventDefault();
        this.dropZone.classList.remove('drag-over');

        const files = event.dataTransfer?.files;
        if (files && files.length > 0 && files[0]) {
            this.handleFile(files[0]);
        }
    }

    /**
     * Handle file input change event
     */
    private handleFileInputChange(event: Event): void {
        const target = event.target as HTMLInputElement;
        const files = target.files;
        if (files && files.length > 0 && files[0]) {
            this.handleFile(files[0]);
        }
    }

    /**
     * Process the selected file
     */
    private async handleFile(file: File): Promise<void> {
        // Validate file
        const validation = this.validateFile(file);
        if (!validation.valid) {
            this.showError(validation.error || 'Invalid file');
            return;
        }

        try {
            // Show progress
            this.showProgress(0);
            this.callbacks.onFileSelected?.(file);

            // Read and parse file
            const words = await this.parseFile(file);
            this.showProgress(50);

            // Validate word count
            if (words.length !== this.config.minWords) {
                throw new Error(`File must contain exactly ${this.config.minWords} words, found ${words.length}`);
            }

            // Simulate upload progress
            await this.simulateUpload();
            this.showProgress(100);

            // Create result
            const result: FileUploadResult = {
                success: true,
                filename: file.name,
                words: words
            };

            this.showSuccess(`Successfully loaded ${words.length} words from ${file.name}`);
            this.callbacks.onFileUploaded?.(result);

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to process file';
            this.showError(errorMessage);
            this.callbacks.onError?.(errorMessage);
        }
    }

    /**
     * Validate the selected file
     */
    private validateFile(file: File): { valid: boolean; error?: string } {
        // Check file size
        if (file.size > this.config.maxFileSize) {
            return {
                valid: false,
                error: `File too large. Maximum size is ${this.config.maxFileSize / 1024 / 1024}MB`
            };
        }

        // Check file type
        if (!this.config.allowedFileTypes.includes(file.type) && 
            !this.config.allowedFileTypes.some(type => {
                const extension = type.split('/')[1];
                return extension && file.name.toLowerCase().endsWith(extension);
            })) {
            return {
                valid: false,
                error: 'Invalid file type. Please upload a TXT or CSV file'
            };
        }

        return { valid: true };
    }

    /**
     * Parse the file content to extract words
     */
    private parseFile(file: File): Promise<string[]> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                try {
                    const content = e.target?.result as string;
                    const words = this.extractWords(content);
                    resolve(words);
                } catch (error) {
                    reject(error);
                }
            };

            reader.onerror = () => {
                reject(new Error('Failed to read file'));
            };

            reader.readAsText(file);
        });
    }

    /**
     * Extract words from file content
     */
    private extractWords(content: string): string[] {
        // Split by various delimiters (comma, newline, semicolon, tab)
        const words = content
            .split(/[,\n\r\t;]+/)
            .map(word => word.trim())
            .filter(word => word.length > 0)
            .map(word => word.replace(/['"]/g, '')); // Remove quotes

        return words;
    }

    /**
     * Simulate upload progress for better UX
     */
    private simulateUpload(): Promise<void> {
        return new Promise((resolve) => {
            let progress = 50;
            const interval = setInterval(() => {
                progress += 10;
                this.showProgress(progress);
                
                if (progress >= 100) {
                    clearInterval(interval);
                    resolve();
                }
            }, 100);
        });
    }

    /**
     * Show upload progress
     */
    private showProgress(percentage: number): void {
        this.progressBar.style.display = 'block';
        const progressFill = this.progressBar.querySelector('.progress-fill') as HTMLElement;
        const progressText = this.progressBar.querySelector('.progress-text') as HTMLElement;
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        
        if (progressText) {
            progressText.textContent = `${Math.round(percentage)}%`;
        }

        this.callbacks.onProgress?.(percentage);

        if (percentage >= 100) {
            setTimeout(() => {
                this.progressBar.style.display = 'none';
            }, 1000);
        }
    }

    /**
     * Show success message
     */
    private showSuccess(message: string): void {
        this.statusMessage.className = 'file-upload-status success';
        this.statusMessage.textContent = message;
        this.statusMessage.style.display = 'block';
    }

    /**
     * Show error message
     */
    private showError(message: string): void {
        this.statusMessage.className = 'file-upload-status error';
        this.statusMessage.textContent = message;
        this.statusMessage.style.display = 'block';
    }

    /**
     * Clear status message
     */
    public clearStatus(): void {
        this.statusMessage.style.display = 'none';
        this.progressBar.style.display = 'none';
    }

    /**
     * Reset the component to initial state
     */
    public reset(): void {
        this.fileInput.value = '';
        this.clearStatus();
        this.dropZone.classList.remove('drag-over');
    }

    /**
     * Enable or disable the component
     */
    public setEnabled(enabled: boolean): void {
        if (enabled) {
            this.dropZone.classList.remove('disabled');
            this.fileInput.disabled = false;
        } else {
            this.dropZone.classList.add('disabled');
            this.fileInput.disabled = true;
        }
    }
}

// Export interfaces for use by other components
export { FileUploadConfig, FileUploadResult, FileUploadCallbacks };
