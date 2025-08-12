#!/bin/bash

# n8n FastAPI Services Startup Script
# This script ensures proper startup order and provides detailed logging

set -e  # Exit on any error

echo "🚀 Starting n8n FastAPI Services..."
echo "=================================="

# Function to check if a service is healthy
check_service_health() {
    local service_name=$1
    local max_wait=60
    local wait_time=0
    
    echo "⏳ Waiting for $service_name to be healthy..."
    
    while [ $wait_time -lt $max_wait ]; do
        if docker compose ps $service_name | grep -q "healthy"; then
            echo "✅ $service_name is healthy!"
            return 0
        fi
        
        echo "⏳ $service_name not ready yet... (${wait_time}s/${max_wait}s)"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    
    echo "❌ $service_name failed to become healthy within ${max_wait}s"
    return 1
}

# Function to check if database is ready
check_database_ready() {
    local max_wait=60
    local wait_time=0
    
    echo "⏳ Waiting for database to be ready..."
    
    while [ $wait_time -lt $max_wait ]; do
        if docker compose exec -T mysql mysql -u n8n_user -pn8n_password -e "USE n8n_feedback; SELECT 1;" >/dev/null 2>&1; then
            echo "✅ Database is ready!"
            return 0
        fi
        
        echo "⏳ Database not ready yet... (${wait_time}s/${max_wait}s)"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    
    echo "❌ Database failed to become ready within ${max_wait}s"
    return 1
}

# Stop any existing services and clean up orphans
echo "🛑 Stopping existing services..."
docker compose down --remove-orphans

# Remove any lingering containers with the same names
echo "🧹 Cleaning up any lingering containers..."
docker rm -f n8n_feedback_db n8n_feedback_backend n8n_feedback_frontend 2>/dev/null || true

# Start MySQL first
echo "🐘 Starting MySQL database..."
docker compose up mysql -d

# Wait for MySQL to be healthy
if ! check_service_health mysql; then
    echo "❌ MySQL failed to start properly"
    docker compose logs mysql
    exit 1
fi

# Give MySQL initialization scripts more time to run
echo "⏳ Waiting for MySQL initialization scripts to complete..."
sleep 10

# Wait for database to be ready (this ensures initialization scripts have completed)
if ! check_database_ready; then
    echo "❌ Database failed to become ready"
    docker compose logs mysql
    exit 1
fi

# Start backend service
echo "🔧 Starting FastAPI backend..."
docker compose up backend -d

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 15

# Check backend logs for any errors
echo "📋 Backend logs:"
docker compose logs --tail=20 backend

# Skip database migrations - user preference
echo "⏭️  Skipping database migrations (user preference)"

# Start frontend service
echo "🌐 Starting React frontend..."
docker compose up frontend -d

# Final status check
echo "📊 Final service status:"
docker compose ps

echo ""
echo "🎉 All services started successfully!"
echo ""
echo "📱 Frontend: http://104.131.8.230:3000"
echo "🔧 Backend API: http://104.131.8.230:8000"
echo "🗄️  Database: localhost:3306"
echo ""
echo "📋 To view logs: docker compose logs -f [service_name]"
echo "🛑 To stop: docker compose down"