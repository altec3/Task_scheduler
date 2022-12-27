FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /server

# Установка зависимостей
COPY poetry.lock .
COPY pyproject.toml .
RUN pip install --no-cache-dir --no-warn-script-location -U pip &&\
    pip install --no-cache-dir --no-warn-script-location poetry &&\
    poetry config virtualenvs.create false &&\
    poetry install

# Копирование файлов проекта
COPY todolist/manage.py .
COPY todolist/core core
COPY todolist/todolist todolist
COPY entrypoint.sh .

# Загрузка фикстур
ENTRYPOINT ["bash", "entrypoint.sh"]
