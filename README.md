# Fincontrol — Локальный финансовый контроль

Local-first финансовый контроль для самозанятых и микробизнеса.

## Стек

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2.x async, PostgreSQL, Redis
- **Frontend:** React 19, TypeScript, Vite, TanStack Query, shadcn/ui, Recharts

## Быстрый старт

```bash
# 1. Поднять PostgreSQL и Redis
make up

# 2. Подождать 3–5 сек, затем миграции
make db-migrate

# 3. Backend (в отдельном терминале)
make backend

# 4. Frontend (в отдельном терминале)
cd frontend && yarn install && yarn dev
```

**Порты по умолчанию** (если 5432/6379 заняты локально): PostgreSQL — 5433, Redis — 6380. В `backend/.env` уже настроено.

**Если ошибка `InvalidPasswordError`** — локальный PostgreSQL с другими учётными данными. Либо сбросить docker БД (`make clean-db && make up`), либо указать в `.env` свои логин/пароль для локального postgres.

## Ручной запуск

### Backend

```bash
cd backend
uv sync
cp .env.example .env
# Убедитесь, что PostgreSQL запущен (make up или docker-compose up -d postgres redis)
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
yarn install
yarn dev
```

### Docker Compose (полный стек)

```bash
docker-compose up -d
```

- Backend: http://localhost:8001
- Swagger: http://localhost:8001/docs
- Frontend: http://localhost:5173

## MVP функции

- Импорт CSV-выписок с мастером сопоставления колонок
- Защита от дублей
- Ручная категоризация операций
- Отчёты по cashflow и категориям
- Базовая налоговая оценка
- Прогноз остатка на 14 дней
- Регулярные платежи
- Экспорт (в разработке)
