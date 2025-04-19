FROM python:3.12.0

# устанавливаем переменные окружения
ENV HOME=/app \
    PYTHONPATH="$PYTHONPATH:/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


# создаем домашнюю директорию для пользователя(/app) и директорию для проекта(/app/store)
# создаем группу fast
# создаем отдельного пользователя fast

WORKDIR $HOME

COPY ./pyproject.toml ./

# Устанавливаем Poetry и зависимости
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root && \
    pip cache purge

# копирование проекта FastAPI в рабочую директорию
COPY . .

ADD alembic.ini .