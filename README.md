# Fincontrol — Локальный финансовый контроль

Local-first финансовый контроль для самозанятых и микробизнеса.

## Стек

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2.x async, PostgreSQL, Redis
- **Frontend:** React 19, TypeScript, Vite, TanStack Query, Dexie (IndexedDB), shadcn/ui, Recharts

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
- Ручная категоризация операций и правила категоризации из БД (плюс эвристики по ключевым словам)
- Отчёты по cashflow и категориям
- Базовая налоговая оценка
- Прогноз остатка на 14 дней
- Регулярные платежи и напоминания (`GET /api/v1/recurring/reminders`)
- Экспорт и импорт JSON-резервной копии: `GET /api/v1/backups/export` (без шифрования), `POST /api/v1/backups/export` с телом `{"passphrase":"…"}` (PBKDF2 + AES-256-GCM), импорт `POST /api/v1/backups/import?replace=true` — голый снимок или `{"passphrase":"…","backup":{…зашифрованный…}}`
- После успешного импорта страница «Резервная копия» вызывает `queryClient.clear()` и очищает IndexedDB read-cache; список категорий с `staleTime: 0`; API и клиентский `fetch` используют `no-store`, чтобы браузер не отдавал старый `GET /categories` из HTTP-кэша.
- **Офлайн:** кэш списков операций/категорий в IndexedDB и очередь PATCH категорий с синхронизацией при появлении сети (см. ниже)

## Офлайн-слой (очередь и кэш чтения)

- Последний успешный ответ **списка операций** (постранично) и **категорий** пишется в **IndexedDB** (библиотека Dexie).
- **Смена категории** при ошибке сети попадает в **очередь** (FIFO, дедупликация по транзакции — последнее значение побеждает). Сброс: событие `online`, загрузка страницы при активной сети или кнопка «Отправить сейчас» в баннере.
- **Конфликты:** ответ **404** на PATCH удаляет соответствующую операцию из очереди; иные ошибки оставляют запись для повторной попытки.
- Только **онлайн:** импорт CSV, авто-категоризация, создание категории; отчёты и прогноз без офлайн-кэша при обрыве сети не загрузятся.

## Ограничения относительно «идеального» local-first

Полноценное ядро без обязательного сервера и **шифрование** содержимого IndexedDB (пароль / Web Crypto) здесь **не сделаны** — кэш и очередь хранятся **в открытом виде**. Для продакшена задайте явные `CORS_ORIGINS` и отключите демо-режим при появлении реальной аутентификации.
