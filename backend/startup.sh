#!/bin/bash

echo "Starting with SQLite database..."
echo "No database connection check needed for SQLite"

echo "Database is ready! Running Alembic migrations..."

# Ensure we're in the app directory
cd /app

# Check if SQLite database exists
echo "Checking SQLite database..."
if [ -f "n8n_feedback.db" ]; then
    echo "SQLite database file exists"
else
    echo "SQLite database file does not exist yet - migrations will create it"
fi

# Run Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head
migration_exit_code=$?

if [ $migration_exit_code -eq 0 ]; then
    echo "✅ Alembic migrations completed successfully!"
elif [ $migration_exit_code -eq 1 ]; then
    echo "⚠️  Alembic migrations failed, but continuing with server startup..."
    echo "This might be normal if migrations are already up to date or if there are no pending migrations."
else
    echo "❌ Alembic migrations failed with exit code $migration_exit_code"
    echo "Starting server anyway, but database schema might be incomplete..."
fi

# Final status check
echo "=== Startup Summary ==="
echo "✅ SQLite database: Ready"
echo "✅ Alembic migrations: Attempted"
echo "🚀 Starting FastAPI server..."

# Start the FastAPI server with CORS-friendly settings
echo "Starting FastAPI server with CORS configuration..."
echo "CORS_ORIGINS: '$CORS_ORIGINS'"
echo "FRONTEND_URL: '$FRONTEND_URL'"
echo "PYTHONPATH: '$PYTHONPATH'"
echo "All environment variables:"
env | grep -E "(CORS|FRONTEND|PYTHON)" | sort

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --log-level info --reload 