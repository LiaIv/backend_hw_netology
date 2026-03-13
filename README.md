# Домашнее задание 4

Решение реализует модель данных на SQLAlchemy для загрузки данных из `students.csv` в SQLite-базу `students.db`.

## Что сделано

- описаны модели `Faculty`, `Student`, `Course`, `GradeRecord`;
- реализован класс `StudentRepository` для операций `INSERT` и `SELECT`;
- добавлен импорт данных из CSV;
- реализованы методы:
  - получения списка студентов по факультету;
  - получения списка уникальных курсов;
  - получения студентов по выбранному курсу с оценкой ниже 30;
  - получения среднего балла по факультету.

## Как запустить

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
