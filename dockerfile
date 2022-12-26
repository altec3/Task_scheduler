FROM python:3.10-slim

ARG DB_NAME="postgres"
ARG DB_USER="postgres"
ARG DB_PASSWORD="postgres"
ARG DB_HOST="localhost"
ARG DJANGO_SK="(-s6z3ftm4ac)&s6!dcg)7@76=t6x=kz=-u2anu7r@bkg7_7g+"
ARG DJANGO_DEBUG=1

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SK="${DJANGO_SK}" \
    DJANGO_DEBUG="${DJANGO_DEBUG}" \
    DB_NAME="${DB_NAME}" \
    DB_USER="${DB_USER}" \
    DB_PASSWORD="${DB_PASSWORD}" \
    DB_HOST="${DB_HOST}"

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
COPY entrypoint.sh entrypoint.sh

# Загрузка фикстур
ENTRYPOINT ["bash", "entrypoint.sh"]

# CMD gunicorn todolist.wsgi 0.0.0.0:8000 -w 4
CMD python manage.py runserver 0.0.0.0:8000
