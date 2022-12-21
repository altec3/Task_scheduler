# Дипломная работа
## Планировщик задач. Итоговая работа по курсу Python-разработчик.

### Стек

python3.10, Django4.1.4, Postgres

### Установка зависимостей

```python
pip install poetry
poetry install
```

### Создание и запуск образа с PostgreSQL

```python
docker run --name psql -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```