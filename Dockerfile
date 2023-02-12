FROM python:3.10-slim as base_image

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.3.1

WORKDIR /tmp

RUN pip install "poetry==$POETRY_VERSION"

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry export --with dep --without dev,test -f requirements.txt -o requirements.dep.txt && \
    poetry export --with dev --without dep,test -f requirements.txt -o requirements.dev.txt && \
    rm poetry.lock pyproject.toml && \
    pip uninstall poetry -y

WORKDIR /server

# Копирование файлов проекта
COPY todolist/manage.py .
COPY todolist/entrypoint.sh .
COPY todolist/bot bot
COPY todolist/core core
COPY todolist/goals goals
COPY todolist/todolist todolist

EXPOSE 8000

# Применение миграций
ENTRYPOINT ["bash", "entrypoint.sh"]


FROM base_image as dep_image

RUN pip install -r /tmp/requirements.dep.txt
CMD ["gunicorn", "todolist.wsgi:application", "-w", "4", "--bind", "0.0.0.0:8000"]


FROM base_image as dev_image

RUN pip install -r /tmp/requirements.dev.txt
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
