# Frontend - NYT Connections Puzzle Assistant

TypeScript-based frontend for the NYT Connections Puzzle Assistant web application.

## Overview

This frontend provides a modern, responsive web interface for users to:
- Upload CSV files containing 16 words for puzzle creation
- Receive AI-generated word grouping recommendations
- Evaluate recommendations as correct/incorrect/one-away
- View session history and track progress

## Technology Stack

- **TypeScript 5.0+**: Type-safe JavaScript with modern ES2020 features
- **HTML5**: Semantic markup with accessibility considerations
- **CSS3**: Modern CSS with Grid, Flexbox, and CSS variables
- **Modules**: ES6 modules for code organization

## Project Structure

```
src/
├── index.html          # Main HTML entry point
├── main.ts            # TypeScript application entry point
├── styles.css         # Main stylesheet with design system
├── components/        # UI components (to be added in later tasks)
└── services/          # API and business logic services (to be added)

tests/
└── e2e/               # End-to-end tests with Playwright

dist/                  # Built assets (generated)
```

## Development Setup

### Prerequisites
- Node.js 18+ and npm
- TypeScript 5.0+

### Installation
```bash
cd frontend
npm install
```

### Development Commands

```bash
# Build TypeScript and assets
npm run build

# Watch mode for development
npm run dev

# Serve the application locally
npm run serve

# Build and serve in one command
npm start

# Clean build artifacts
npm run clean
```

### Development Server
After running `npm start`, the application will be available at:
- **Frontend**: http://localhost:8080

## Build Process

1. **TypeScript Compilation**: `src/main.ts` → `dist/main.js`
2. **Asset Copying**: HTML and CSS files copied to `dist/`
3. **Source Maps**: Generated for debugging

## Code Style & Standards

- **TypeScript**: Strict mode enabled with comprehensive type checking
- **ES2020**: Modern JavaScript features with ES modules
- **CSS**: BEM methodology with CSS custom properties
- **Accessibility**: WCAG 2.1 AA compliance targeted
- **Responsive Design**: Mobile-first approach with breakpoints at 768px and 480px

## Component Architecture

Components will be implemented in later tasks following this pattern:
- **T041**: File upload component with drag-and-drop
- **T042**: Puzzle display component
- **T043**: Recommendation display cards
- **T044**: Evaluation button components
- **T045**: Session status display
- **T046**: History view component

## API Integration

The frontend communicates with the FastAPI backend via:
- **REST API**: Standard HTTP requests for CRUD operations
- **WebSocket**: Real-time updates for recommendations and evaluations
- **File Upload**: Multipart form data for puzzle CSV files

## Future Enhancements

Components and services to be added in subsequent implementation tasks:
- TypeScript interfaces for API data models
- Service layer for API communication
- WebSocket client for real-time updates
- State management for game sessions
- Error handling and user feedback systems

## Testing

End-to-end tests will be implemented using Playwright:
- File upload workflows
- Recommendation evaluation processes
- Complete game session scenarios

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Goals

- Initial page load: <1 second
- Component interactions: <100ms response time
- File upload feedback: Immediate visual response
- AI recommendation display: <2 seconds from backend
