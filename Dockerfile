FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Сначала копируем только файлы зависимостей и устанавливаем их
# Это позволяет кэшировать слой с зависимостями
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-ansi --no-root

# Теперь копируем исходный код
COPY src ./src

# Устанавливаем проект (без повторной установки зависимостей)
RUN poetry install --no-ansi

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "hw2.main:app", "--host", "0.0.0.0", "--port", "8000"]