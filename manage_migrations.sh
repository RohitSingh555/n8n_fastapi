#!/bin/bash

# Database Migration Management Script for n8n FastAPI
# This script handles database migrations using Alembic

set -e  # Exit on any error

echo "🗄️  Database Migration Manager"
echo "=============================="

# Function to check if backend is running
check_backend_running() {
    if docker compose ps backend | grep -q "Up"; then
        return 0
    else
        return 1
    fi
}

# Function to run migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    
    if ! check_backend_running; then
        echo "❌ Backend service is not running. Please start services first."
        exit 1
    fi
    
    # Run migrations
    docker compose exec -T backend alembic upgrade head
    
    if [ $? -eq 0 ]; then
        echo "✅ Database migrations completed successfully"
    else
        echo "❌ Database migrations failed"
        echo "📋 Migration logs:"
        docker compose logs --tail=20 backend
        exit 1
    fi
}

# Function to create a new migration
create_migration() {
    local message=$1
    
    if [ -z "$message" ]; then
        echo "❌ Please provide a migration message"
        echo "Usage: $0 create 'migration message'"
        exit 1
    fi
    
    echo "📝 Creating new migration: $message"
    
    if ! check_backend_running; then
        echo "❌ Backend service is not running. Please start services first."
        exit 1
    fi
    
    # Create new migration
    docker compose exec -T backend alembic revision --autogenerate -m "$message"
    
    if [ $? -eq 0 ]; then
        echo "✅ Migration created successfully"
        echo "📁 Check the alembic/versions/ directory for the new migration file"
    else
        echo "❌ Failed to create migration"
        exit 1
    fi
}

# Function to show migration status
show_status() {
    echo "📊 Migration Status:"
    
    if ! check_backend_running; then
        echo "❌ Backend service is not running. Please start services first."
        exit 1
    fi
    
    docker compose exec -T backend alembic current
    echo ""
    echo "📋 Migration History:"
    docker compose exec -T backend alembic history
}

# Function to rollback migrations
rollback_migrations() {
    local target=$1
    
    if [ -z "$target" ]; then
        echo "❌ Please specify target revision for rollback"
        echo "Usage: $0 rollback <revision_id>"
        echo "Use '$0 status' to see available revisions"
        exit 1
    fi
    
    echo "🔄 Rolling back to revision: $target"
    
    if ! check_backend_running; then
        echo "❌ Backend service is not running. Please start services first."
        exit 1
    fi
    
    # Confirm rollback
    read -p "Are you sure you want to rollback to revision $target? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Rollback cancelled"
        exit 1
    fi
    
    # Rollback migrations
    docker compose exec -T backend alembic downgrade $target
    
    if [ $? -eq 0 ]; then
        echo "✅ Rollback completed successfully"
    else
        echo "❌ Rollback failed"
        exit 1
    fi
}

# Main script logic
case "${1:-}" in
    "run"|"upgrade")
        run_migrations
        ;;
    "create")
        create_migration "$2"
        ;;
    "status")
        show_status
        ;;
    "rollback"|"downgrade")
        rollback_migrations "$2"
        ;;
    "help"|"-h"|"--help"|"")
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  run, upgrade     Run all pending migrations"
        echo "  create <msg>     Create a new migration with message"
        echo "  status           Show current migration status and history"
        echo "  rollback <rev>   Rollback to specific revision"
        echo "  help             Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 run                    # Run all migrations"
        echo "  $0 create 'add user table' # Create new migration"
        echo "  $0 status                 # Show migration status"
        echo "  $0 rollback abc123        # Rollback to revision abc123"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
