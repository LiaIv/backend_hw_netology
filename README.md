# Домашнее задание 5

В этом задании на основе прошлого проекта добавлен REST API на FastAPI для работы с данными студентов и оценок.

Используются:
- `FastAPI`
- `SQLAlchemy`
- `SQLite`

Что есть в проекте:
- модели `Faculty`, `Student`, `Course`, `GradeRecord`
- репозиторий для работы с базой
- импорт данных из `students.csv`
- CRUD для записей с оценками

## Как запустить

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

После запуска можно открыть:
- `http://127.0.0.1:8000/docs` - Swagger UI
- `http://127.0.0.1:8000/records` - список записей

Основные эндпоинты:
- `POST /records`
- `GET /records`
- `GET /records/{id}`
- `PUT /records/{id}`
- `DELETE /records/{id}`
