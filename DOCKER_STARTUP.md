# Docker Startup Guide for n8n FastAPI

This guide explains how to start and manage the n8n FastAPI services using Docker.

## 🚀 Quick Start

### 1. Start All Services
```bash
docker compose up -d
```

This will start:
- **MySQL Database** (port 3306)
- **FastAPI Backend** (port 8000)
- **React Frontend** (port 3000)

### 2. Check Service Status
```bash
docker compose ps
```

### 3. View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f mysql
docker compose logs -f frontend
```

## 🗄️ Database Management

### Run Database Migrations
```bash
docker compose exec backend alembic upgrade head
```

### Reset Database (if needed)
```bash
# Stop services
docker compose down

# Remove database volume
docker volume rm n8n_fastapi_mysql_data

# Start fresh
docker compose up -d

# Run migrations
docker compose exec backend alembic upgrade head
```

### Check Database Tables
```bash
docker compose exec mysql mysql -u n8n_user -pn8n_password -e "USE n8n_feedback; SHOW TABLES;"
```

## 🛠️ Service Management

### Stop Services
```bash
docker compose down
```

### Restart Services
```bash
docker compose restart
```

### Rebuild and Start
```bash
# Rebuild images
docker compose build

# Start services
docker compose up -d
```

### Update Services
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

## 🔧 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker compose logs

# Check container status
docker compose ps -a

# Restart specific service
docker compose restart backend
```

### Database Connection Issues
```bash
# Check MySQL logs
docker compose logs mysql

# Test database connection
docker compose exec backend python -c "from app.database import engine; print('Connected' if engine.connect() else 'Failed')"
```

### Port Conflicts
If ports are already in use:
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :3306

# Stop conflicting services or change ports in docker-compose.yml
```

## 📍 Service URLs

- **Frontend**: http://104.131.8.230:3000
- **Backend API**: http://104.131.8.230:8000
- **API Docs**: http://104.131.8.230:8000/docs
- **Database**: localhost:3306

## 🐳 Docker Commands Reference

### Container Management
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a specific container
docker stop container_name

# Remove a container
docker rm container_name

# Execute command in running container
docker exec -it container_name bash
```

### Volume Management
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect volume_name

# Remove volume
docker volume rm volume_name
```

### Image Management
```bash
# List images
docker images

# Remove image
docker rmi image_name

# Clean up unused images
docker image prune
```

## 🔍 Monitoring

### Resource Usage
```bash
# Container resource usage
docker stats

# System resource usage
docker system df
```

### Health Checks
```bash
# Check service health
docker compose ps

# Health check logs
docker compose exec backend curl -f http://localhost:8000/health
```

## 📝 Environment Variables

Key environment variables (set in docker-compose.yml):
- `DATABASE_URL`: MySQL connection string
- `MYSQL_ROOT_PASSWORD`: MySQL root password
- `MYSQL_USER`: MySQL user for application
- `MYSQL_PASSWORD`: MySQL password for application

## 🚨 Emergency Procedures

### Complete Reset
```bash
# Stop and remove everything
docker compose down -v --remove-orphans
docker system prune -a --volumes

# Start fresh
docker compose up -d
docker compose exec backend alembic upgrade head
```

### Backup Database
```bash
# Create backup
docker compose exec mysql mysqldump -u n8n_user -pn8n_password n8n_feedback > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker compose exec -T mysql mysql -u n8n_user -pn8n_password n8n_feedback < backup_file.sql
```

## 📚 Additional Resources

- **Docker Compose**: https://docs.docker.com/compose/
- **Alembic**: https://alembic.sqlalchemy.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **MySQL**: https://dev.mysql.com/doc/

---

**Note**: Always ensure Docker and Docker Compose are installed and running before executing these commands.
