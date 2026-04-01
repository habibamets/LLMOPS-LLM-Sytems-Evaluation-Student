build:
	@echo "🏗️  Building Docker images..."
	docker compose build

up:
	@echo "🚀 Starting RAGOPS services..."
	docker compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ RAGOPS is ready!"
	@echo "   Backend: http://localhost:18000"
	@echo "   Health:  http://localhost:18000/health"

down:
	@echo "⏹️  Stopping RAGOPS services..."
	docker compose down

restart:
	@echo "🔄 Restarting RAGOPS services..."
	docker compose down
	docker compose up -d

logs:
	@echo "📄 Showing service logs..."
	docker-compose logs -f backend

links:
	@echo "   Meilisearch: http://localhost:7700"
	@echo "   Backend: http://localhost:18000"
	@echo "   Health:  http://localhost:18000/health"