# CFA CRM + Telegram Mini App MVP

Монорепозиторий MVP для сопровождения CFA-сделок:

- `backend` - FastAPI, SQLAlchemy, PostgreSQL, Alembic.
- `frontend` - Next.js, React, Tailwind, shadcn-style UI.
- `bot` - базовая заготовка aiogram 3.

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и настройте значения.
2. Запустите PostgreSQL:

```bash
docker compose up -d postgres
```

3. Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

4. Frontend:

```bash
cd frontend
npm install
npm run dev
```

5. Bot:

```bash
cd bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Основные зоны

- Admin UI: `http://localhost:3000/admin`
- Telegram Mini App UI: `http://localhost:3000/app`
- API docs: `http://localhost:8000/docs`

## MVP-ограничения

- Генерация документов оставлена как управляемое состояние/заглушка: документы может создавать только роль `manager`, `admin` или `director`.
- Telegram авторизация Mini App подготовлена на уровне интерфейса и backend-моделей, но без проверки Telegram init data.
- Файлы документов сохраняются локально в `backend/storage`.
