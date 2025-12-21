"""
Тесты для модуля train.
"""
import pytest

from hw2.train import _load_data, train_model


class TestLoadData:
    """Тесты для функции загрузки данных."""

    def test_load_data_returns_correct_shapes(self):
        """Проверяем, что данные загружаются с правильными размерностями."""
        X_train, X_test, y_train, y_test = _load_data()

        # Iris dataset: 150 samples, 80/20 split
        assert X_train.shape[0] == 120
        assert X_test.shape[0] == 30
        assert X_train.shape[1] == 4  # 4 признака
        assert len(y_train) == 120
        assert len(y_test) == 30


class TestTrainModel:
    """Тесты для функции обучения модели."""

    def test_train_logreg_with_mock_mlflow(self, mock_mlflow):
        """
        Тест обучения логистической регрессии с моком MLflow.
        Проверяем, что модель сохраняется в S3 (через MLflow).
        """
        result = train_model(model_type="logreg", C=0.5)

        # Проверяем структуру результата
        assert "run_id" in result
        assert result["run_id"] == "test-run-id-12345"
        assert "metrics" in result
        assert "accuracy" in result["metrics"]
        assert 0 <= result["metrics"]["accuracy"] <= 1

        # Проверяем, что модель была залогирована (сохранена в S3)
        mock_mlflow["log_model"].assert_called_once()
        call_kwargs = mock_mlflow["log_model"].call_args
        assert call_kwargs.kwargs["artifact_path"] == "model"

    def test_train_rf_with_mock_mlflow(self, mock_mlflow):
        """
        Тест обучения Random Forest с моком MLflow.
        Проверяем работу с другим типом модели.
        """
        result = train_model(model_type="rf", n_estimators=10)

        assert result["run_id"] == "test-run-id-12345"
        assert result["params"]["model_type"] == "rf"
        assert result["params"]["n_estimators"] == 10

        # Модель должна быть сохранена
        mock_mlflow["log_model"].assert_called_once()

    def test_train_unknown_model_raises_error(self, mock_mlflow):
        """Тест на неизвестный тип модели."""
        with pytest.raises(ValueError, match="Unknown model_type"):
            train_model(model_type="unknown_model")


class TestS3Integration:
    """Тесты для проверки интеграции с S3 (с моками)."""

    def test_s3_client_mock_put_object(self, mock_s3_client):
        """
        Тест мока S3 клиента для сохранения объекта.
        Демонстрирует использование фикстуры mock_s3_client.
        """
        # Симулируем сохранение модели в S3
        response = mock_s3_client.put_object(
            Bucket="mlflow",
            Key="models/test-model.pkl",
            Body=b"fake_model_data"
        )

        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        mock_s3_client.put_object.assert_called_once_with(
            Bucket="mlflow",
            Key="models/test-model.pkl",
            Body=b"fake_model_data"
        )

    def test_s3_client_mock_list_objects(self, mock_s3_client):
        """
        Тест мока S3 клиента для листинга объектов.
        """
        response = mock_s3_client.list_objects_v2(Bucket="mlflow", Prefix="model/")

        assert "Contents" in response
        assert len(response["Contents"]) == 1
        assert response["Contents"][0]["Key"] == "model/model.pkl"

