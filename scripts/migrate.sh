#!/bin/bash

# Database migration script
echo "🗄️  Running database migrations..."

# Check if services are running
if ! docker-compose ps | grep -q "server.*Up"; then
    echo "❌ Server is not running. Please start services first with: docker-compose up -d"
    exit 1
fi

# Run migrations
echo "📝 Applying database migrations..."
docker-compose exec server alembic upgrade head

# Check migration status
echo "✅ Migration status:"
docker-compose exec server alembic current

echo "✅ Migrations completed!"

