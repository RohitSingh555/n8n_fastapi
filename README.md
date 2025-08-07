# n8n Execution Feedback System

A modern, full-stack application for collecting and managing feedback for n8n execution results. Built with FastAPI backend and React frontend with a beautiful, minimalist design.

## Features

### Backend (FastAPI)
- **POST** `/api/feedback` - Create new feedback submissions
- **GET** `/api/feedback/{submission_id}` - Retrieve specific feedback by ID
- **GET** `/api/feedback` - List all feedback submissions with pagination
- **GET** `/api/feedback/execution/{execution_id}` - Get feedback by n8n execution ID
- **PUT** `/api/feedback/{submission_id}` - Update existing feedback submissions
- **Health check** endpoints for monitoring

### Frontend (React)
- **Modern, minimalist design** with shadcn-style aesthetics
- **Tabbed interface** for better organization (LinkedIn, X/Twitter, Images)
- **Pre-filled content** for easy review and feedback
- **Edit mode** - Load and update existing feedback
- **Create new** functionality after editing
- **Responsive design** that works on all devices
- **Beautiful gradients** and glass-morphism effects
- **Smooth animations** and transitions

## Key Improvements

### PUT Endpoint
- **Partial updates** - Only update the fields you provide
- **Automatic timestamp** - `updated_at` field is automatically set
- **Error handling** - Proper validation and error responses
- **Idempotent** - Safe to call multiple times

### Frontend Design
- **Subtle, minimalist aesthetic** inspired by shadcn/ui
- **Dark theme** with gradient backgrounds
- **Glass-morphism effects** with backdrop blur
- **Improved typography** and spacing
- **Better form organization** with tabs
- **Enhanced user experience** with clear visual feedback

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Testing the PUT Endpoint
```bash
python test_put_endpoint.py
```

## API Usage Examples

### Create Feedback
```bash
curl -X POST "http://localhost:8000/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "n8n_execution_id": "exec-123",
    "email": "user@example.com",
    "linkedin_feedback": "Great content!",
    "linkedin_chosen_llm": "Grok"
  }'
```

### Update Feedback
```bash
curl -X PUT "http://localhost:8000/api/feedback/{submission_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "linkedin_feedback": "Updated feedback",
    "linkedin_chosen_llm": "o3"
  }'
```

### Get Feedback
```bash
curl "http://localhost:8000/api/feedback/{submission_id}"
```

## Frontend Features

### Edit Mode
1. Enter a submission ID in the "Load Existing Feedback" section
2. Click "Load" to populate the form with existing data
3. Make your changes
4. Click "Update Feedback" to save changes

### Create New
- After editing, click "Create New" to start fresh
- All pre-filled content will be restored to defaults

### Tabbed Interface
- **LinkedIn Content** - Review and provide feedback for LinkedIn posts
- **X/Twitter Content** - Review and provide feedback for X/Twitter posts  
- **Generated Images** - Review and provide feedback for generated images

## Database Schema

The system uses SQLAlchemy with automatic timestamp management:
- `created_at` - Set automatically on creation
- `updated_at` - Updated automatically on PUT requests

## Development

### Running Tests
```bash
cd backend
python -m pytest tests/
```

### Database Migrations
```bash
cd backend
alembic upgrade head
```

## Technologies Used

- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic
- **Frontend**: React, Tailwind CSS, React Icons, Axios
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Styling**: Custom Tailwind configuration with glass-morphism effects

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
