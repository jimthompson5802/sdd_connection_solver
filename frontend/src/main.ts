/**
 * Main TypeScript entry point for NYT Connections Puzzle Assistant Frontend
 * 
 * This module initializes the full application using the App class
 * with all implemented components (T041-T046).
 */

import { App } from './App';
import './styles.css';

/**
 * Initialize the full application with all components
 */
async function initializeApp(): Promise<void> {
  console.log('NYT Connections Puzzle Assistant - Starting Full Application...');
  
  try {
    // Create and initialize the main App instance
    const app = new App('app', {
      // Use App defaults (apiBaseUrl: 'http://localhost:8000/api/v1', wsBaseUrl: 'ws://localhost:8000')
      // or rely on dev-server proxy when using relative paths from ApiService
      debugMode: true,
      autoConnect: true
    });

    // Initialize the application
    await app.init();
    
    console.log('Application initialized successfully with all components');
    
    // Make app instance available globally for debugging
    (window as any).app = app;
    
  } catch (error) {
    console.error('Failed to initialize application:', error);
    
    // Show error in the app container
    const appElement = document.getElementById('app');
    if (appElement) {
      appElement.innerHTML = `
        <div class="error-container">
          <h1>Application Error</h1>
          <p>Failed to initialize the NYT Connections Puzzle Assistant.</p>
          <p>Error: ${error instanceof Error ? error.message : 'Unknown error'}</p>
          <p>Please check the console for more details.</p>
        </div>
      `;
    }
  }
}

/**
 * Setup event listeners for application startup
 */
function setupEventListeners(): void {
  // Initialize immediately if DOM is already loaded, otherwise wait for DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      console.log('DOM content loaded - initializing app...');
      initializeApp();
    });
  } else {
    console.log('DOM already loaded - initializing app immediately...');
    initializeApp();
  }

  // Handle window resize for responsive design
  window.addEventListener('resize', () => {
    console.log('Window resized');
    // The App class will handle responsive updates
  });
}

// Setup event listeners when script loads
setupEventListeners();

// Export for potential use by other modules
export { initializeApp };
