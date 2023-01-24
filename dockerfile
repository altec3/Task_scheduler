FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /server

EXPOSE 8000

# Установка зависимостей
COPY poetry.lock .
COPY pyproject.toml .
RUN pip install --no-cache-dir --no-warn-script-location -U pip &&\
    pip install --no-cache-dir --no-warn-script-location poetry &&\
    poetry config virtualenvs.create false &&\
    poetry install --without dev --no-root

# Копирование файлов проекта
COPY todolist/todolist todolist
COPY todolist/core core
COPY todolist/goals goals
COPY todolist/manage.py .
COPY entrypoint.sh .

# Применение миграций
ENTRYPOINT ["bash", "entrypoint.sh"]
