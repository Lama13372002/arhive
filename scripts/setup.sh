#!/bin/bash

# Sunog Setup Script
echo "🎵 Setting up Sunog - AI Song Generator"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your actual API keys and configuration"
fi

# Create SSL directory
mkdir -p infra/ssl

# Generate self-signed SSL certificate for development
if [ ! -f infra/ssl/cert.pem ]; then
    echo "🔐 Generating self-signed SSL certificate..."
    openssl req -x509 -newkey rsa:4096 -keyout infra/ssl/key.pem -out infra/ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Build and start services
echo "🚀 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec server alembic upgrade head

# Create MinIO bucket
echo "📦 Creating MinIO bucket..."
docker-compose exec minio mc mb /data/sunog-assets || true

echo "✅ Setup complete!"
echo ""
echo "🌐 Services available at:"
echo "  - Frontend: http://localhost:3000"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3001 (admin/admin)"
echo ""
echo "📋 Next steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Set up your Telegram bot webhook"
echo "  3. Configure your domain and SSL certificates for production"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose logs -f [service]"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart [service]"

