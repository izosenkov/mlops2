"""
Фикстуры для тестов.
"""
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_mlflow(mocker):
    """
    Фикстура для мока MLflow.
    Мокает все вызовы MLflow, включая сохранение модели в S3.
    """
    # Мокаем mlflow.start_run
    mock_run = MagicMock()
    mock_run.__enter__ = MagicMock(return_value=MagicMock(
        info=MagicMock(run_id="test-run-id-12345")
    ))
    mock_run.__exit__ = MagicMock(return_value=False)

    mocker.patch("hw2.train.mlflow.start_run", return_value=mock_run)
    mocker.patch("hw2.train.mlflow.log_param")
    mocker.patch("hw2.train.mlflow.log_metric")

    # Мокаем сохранение модели в S3
    mock_log_model = mocker.patch("hw2.train.mlflow.sklearn.log_model")

    return {
        "start_run": mock_run,
        "log_model": mock_log_model,
    }


@pytest.fixture
def mock_s3_client(mocker):
    """
    Фикстура для мока S3/MinIO клиента (boto3).
    Используется для тестирования прямой работы с S3.
    """
    mock_client = MagicMock()
    mock_client.put_object = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})
    mock_client.get_object = MagicMock(return_value={
        "Body": MagicMock(read=MagicMock(return_value=b"model_data"))
    })
    mock_client.list_objects_v2 = MagicMock(return_value={
        "Contents": [{"Key": "model/model.pkl"}]
    })

    mocker.patch("boto3.client", return_value=mock_client)

    return mock_client

