# n8n Execution Feedback System

A FastAPI + React application for collecting and storing feedback on n8n execution results, including LinkedIn content, X content, and image generation feedback.

## 🚀 Quick Start with Docker

The easiest way to run this application is using Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd n8n_automate

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📁 Project Structure

```
n8n_automate/
├── docker-compose.yml      # Docker orchestration
├── backend/                # FastAPI backend
│   ├── Dockerfile         # Backend container
│   ├── app/
│   │   ├── models.py      # Database models
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── database.py    # Database configuration
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── alembic/           # Database migrations
└── frontend/              # React frontend
    ├── Dockerfile         # Frontend container
    ├── src/
    │   ├── App.js         # Main React component
    │   └── index.css      # Tailwind CSS styles
    ├── package.json       # Node dependencies
    └── tailwind.config.js # Tailwind configuration
```

## 🎯 Features

- **Docker-first setup** with PostgreSQL, FastAPI, and React containers
- Store n8n execution feedback with unique submission IDs
- Collect feedback for LinkedIn content (Grok, o3, Gemini)
- Collect feedback for X content (Grok, o3, Gemini)  
- Collect feedback for images (Stable Diffusion, Pixabay, GPT1)
- Modern React UI with Tailwind CSS and react-icons
- Pre-filled content from n8n executions
- User-friendly feedback forms with dropdowns

## 🐳 Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

3. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

### Database Migrations

To run database migrations in Docker:

```bash
# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"

# Apply migrations
docker-compose exec backend alembic upgrade head
```

### Running Tests

To run the comprehensive test suite:

```bash
# Run tests in Docker
docker-compose exec backend python run_tests.py

# Or run tests directly
docker-compose exec backend pytest tests/ -v

# Run specific test file
docker-compose exec backend pytest tests/test_api.py -v

# Run tests with coverage
docker-compose exec backend pytest tests/ --cov=app --cov-report=html
```

## 🔧 Manual Setup (Alternative)

### Backend Setup
1. Navigate to backend directory
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up PostgreSQL database
6. Run migrations: `alembic upgrade head`
7. Start FastAPI server: `uvicorn app.main:app --reload`

### Frontend Setup
1. Navigate to frontend directory
2. Install dependencies: `npm install`
3. Install Tailwind CSS: `npm install -D tailwindcss autoprefixer postcss`
4. Start development server: `npm start`

## 📡 API Endpoints

- `POST /api/feedback` - Submit feedback data
- `GET /api/feedback/{submission_id}` - Get feedback by submission ID
- `GET /api/feedback` - Get all feedback submissions
- `GET /api/feedback/execution/{execution_id}` - Get feedback by n8n execution ID
- `GET /health` - Health check endpoint

## 🎨 UI Features

- **Matte finish design** with dark background (#0c0d0f)
- **Responsive layout** that works on all devices
- **Pre-filled content** from n8n executions
- **Interactive forms** with real-time validation
- **Success/error messages** with icons
- **Loading states** for better UX
- **Image previews** for generated images

## 🔍 Database Schema

The application stores feedback data in PostgreSQL with the following structure:

- **n8n_execution_id**: Links feedback to specific n8n execution
- **LinkedIn content**: Grok, o3, and Gemini generated content
- **X content**: Grok, o3, and Gemini generated content  
- **Image URLs**: Stable Diffusion, Pixabay, and GPT1 image URLs
- **User feedback**: Text feedback for each content type
- **LLM selections**: User's preferred LLM for each content type
- **Custom content**: User-generated custom content
- **Timestamps**: Creation and update timestamps

## 🛠️ Development

### Adding New Features
1. Update the database model in `backend/app/models.py`
2. Create and run Alembic migrations
3. Update Pydantic schemas in `backend/app/schemas.py`
4. Add API endpoints in `backend/app/main.py`
5. Update React components in `frontend/src/App.js`

### Environment Variables
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost/n8n_feedback
```

## 📝 License

This project is licensed under the MIT License.
