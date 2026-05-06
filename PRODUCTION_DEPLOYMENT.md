# 🚀 Production Deployment Configuration

## Environment Variables

Buat file `.env` di root project untuk production:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_URL=https://api.niscahya.com

# CORS Settings
CORS_ORIGINS=https://niscahya.com,https://www.niscahya.com

# Database
DATABASE_URL=sqlite:///./niscahya_prod.db

# Vector Store
VECTOR_STORE_PATH=./chroma_db_prod

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-3.5-turbo

# Security
SECRET_KEY=your_secret_key_here
DEBUG=False
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  niscahya-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_URL=https://api.niscahya.com
      - CORS_ORIGINS=https://niscahya.com,https://www.niscahya.com
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./chroma_db_prod:/app/chroma_db_prod
      - ./uploads_prod:/app/uploads_prod
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - niscahya-api
    restart: unless-stopped
```

### Nginx Configuration

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server niscahya-api:8000;
    }

    server {
        listen 80;
        server_name api.niscahya.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.niscahya.com;

        ssl_certificate /etc/ssl/certs/niscahya.crt;
        ssl_certificate_key /etc/ssl/certs/niscahya.key;

        # SSL Configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # API Proxy
        location / {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # CORS headers
            add_header 'Access-Control-Allow-Origin' 'https://niscahya.com' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;

            # Handle preflight requests
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## Production Checklist

### ✅ Pre-Deployment
- [ ] Update API_URL in environment variables
- [ ] Configure CORS origins for your domain
- [ ] Set up SSL certificates
- [ ] Test API endpoints locally
- [ ] Backup existing database/vector store

### ✅ Deployment Steps
- [ ] Build Docker image: `docker-compose build`
- [ ] Start services: `docker-compose up -d`
- [ ] Check health endpoint: `curl https://api.niscahya.com/health`
- [ ] Test API documentation: `https://api.niscahya.com/docs`
- [ ] Update frontend to use production API URL

### ✅ Post-Deployment
- [ ] Test chatbot integration on website
- [ ] Monitor API logs for errors
- [ ] Set up monitoring/alerts
- [ ] Configure backup strategy
- [ ] Update DNS if needed

## Monitoring & Maintenance

### Health Check Endpoint

API menyediakan health check di `/health`:

```bash
curl https://api.niscahya.com/health
# Should return: {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
```

### Log Monitoring

```bash
# View container logs
docker-compose logs -f niscahya-api

# View nginx logs
docker-compose logs -f nginx
```

### Backup Strategy

```bash
# Backup database and vector store
docker exec niscahya-api tar czf /backup/backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    /app/chroma_db_prod \
    /app/uploads_prod \
    /app/niscahya_prod.db
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (nginx) for multiple API instances
- Implement Redis for session storage
- Consider database migration to PostgreSQL

### Performance Optimization
- Enable gzip compression
- Implement caching for static responses
- Use CDN for uploaded files
- Monitor response times and optimize slow queries

## Security Best Practices

### API Security
- Use HTTPS only
- Implement rate limiting
- Validate input data
- Use API keys for admin endpoints
- Regular security updates

### Data Protection
- Encrypt sensitive data
- Regular backups
- Secure file uploads
- GDPR compliance for user data

---

## Quick Deploy Script

```bash
#!/bin/bash

# Production deployment script
echo "🚀 Starting production deployment..."

# Build and deploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
sleep 30

# Health check
if curl -f https://api.niscahya.com/health; then
    echo "✅ Deployment successful!"
    echo "📊 API URL: https://api.niscahya.com"
    echo "📚 Docs: https://api.niscahya.com/docs"
else
    echo "❌ Deployment failed!"
    docker-compose logs niscahya-api
    exit 1
fi
```