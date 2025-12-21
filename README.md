# MLOps HW2 + остальное из 3его

## Запуск

1. Использовать `.env` уже из проекта или cкопировать `.env.example` в `.env`, можно поменять пароли
```bash
cp .env.example .env
```

2. Собрать все:
```bash
docker-compose build
```

3. Запустить:
```bash
docker-compose up
```

## Сервисы

- **FastAPI**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **MLflow UI**: http://localhost:5001
- **MinIO Console**: http://localhost:9001

## Хранение

Модели сохраняются через MLflow в s3 совместимое хранилизе.
Артефакты находятся в бакете `mlflow` по адресу `s3://mlflow/`.

MinIO Console берет логин/пароль из `.env` файла (по умолчанию: minio / minio123)

## Makefile

Доступные команды:

```bash
#автотесты
make test

# линтер
make lint

# Сборка Docker образа и пуш в DockerHub
make build-push DOCKER_USERNAME=your-username
```

## Тесты

Unit-тесты находятся в папке `tests/`. Используются моки и фикстуры для изоляции от внешних зависимостей (MLflow, S3).

Запуск тестов локально:
```bash
poetry install
make test
```

Структура тестов:
- `tests/conftest.py` — фикстуры (`mock_mlflow`, `mock_s3_client`)
- `tests/test_train.py` — тесты обучения моделей

