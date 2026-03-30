.PHONY: up down db-migrate backend frontend dev clean-db

clean-db:
	docker-compose down -v

up:
	docker-compose up -d postgres redis

down:
	docker-compose down

db-migrate:
	cd backend && uv run alembic upgrade head

backend:
	cd backend && uv run uvicorn app.main:app --reload

frontend:
	cd frontend && yarn dev

dev: up
	@echo "Waiting for PostgreSQL..."
	@sleep 3
	$(MAKE) db-migrate
	@echo "Run 'make backend' and 'make frontend' in separate terminals"
