# Домашнее задание 7

В этом задании к CRUD-сервису на FastAPI добавлен сервис аутентификации.

Используются:
- `FastAPI`
- `SQLAlchemy`
- `SQLite`

Что есть в проекте:
- модели `Faculty`, `Student`, `Course`, `GradeRecord`
- модель `User`
- репозиторий для работы с базой
- импорт данных из `students.csv`
- CRUD для записей с оценками
- маршрутизатор `/auth` для регистрации, входа и выхода
- защита CRUD-эндпоинтов по идентификатору пользователя

## Как запустить

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

После запуска можно открыть:
- `http://127.0.0.1:8000/docs` - Swagger UI

## Аутентификация

Сначала нужно зарегистрировать пользователя:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"12345"}'
```

Затем выполнить вход:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"12345"}'
```

В ответе будет `user_id`. Его нужно передавать в заголовке `X-User-Id`:

```bash
curl http://127.0.0.1:8000/records -H "X-User-Id: 1"
```

Чтобы завершить сессию:

```bash
curl -X POST http://127.0.0.1:8000/auth/logout -H "X-User-Id: 1"
```

Без активного пользователя защищенные эндпоинты возвращают `401 Unauthorized`.

Основные эндпоинты:
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `POST /records`
- `GET /records`
- `GET /records/{id}`
- `PUT /records/{id}`
- `DELETE /records/{id}`
