# FastAPI Application Setup

## Running the Application

The FastAPI application has been set up with comprehensive middleware and proper configuration.

### Development Server

To run the development server:

```bash
# From the project root directory
cd /path/to/sdd_connection_solver
source venv/bin/activate
uvicorn backend.src.main:app --host 127.0.0.1 --port 8000 --reload
```

### Available Endpoints

- **Root**: `GET /` - Basic API information
- **Health Check**: `GET /health` - Application health status and system metrics
- **API Documentation**: `GET /docs` - Interactive Swagger UI documentation
- **Alternative Docs**: `GET /redoc` - Alternative documentation interface

### API Endpoints

#### Puzzle Endpoints
- `POST /api/v1/puzzles/upload` - Upload puzzle file
- `GET /api/v1/puzzles/{puzzle_id}` - Get puzzle details

#### Session Endpoints  
- `POST /api/v1/sessions` - Create new game session
- `GET /api/v1/sessions/{session_id}` - Get session state

#### Recommendation Endpoints
- `POST /api/v1/sessions/{session_id}/recommendations` - Generate AI recommendation
- `GET /api/v1/sessions/{session_id}/recommendations` - Get current recommendation
- `POST /api/v1/sessions/{session_id}/recommendations/{recommendation_id}/evaluate` - Evaluate recommendation

#### History Endpoints
- `GET /api/v1/sessions/{session_id}/history` - Get recommendation history

### Configuration

The application includes:

- **CORS Middleware**: Configured for frontend development servers (localhost:3000, localhost:5173)
- **Trusted Host Middleware**: Security middleware for allowed hosts
- **Request Logging**: All requests and responses are logged with processing time
- **Error Handling**: Comprehensive exception handling with structured error responses
- **Health Monitoring**: System metrics including CPU and memory usage

### Testing

Test the setup with:

```bash
# Test basic connectivity
curl http://127.0.0.1:8000/

# Test health endpoint
curl http://127.0.0.1:8000/health

# View interactive documentation
open http://127.0.0.1:8000/docs
```
