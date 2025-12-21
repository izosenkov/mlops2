import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from .logger import get_logger

logger = get_logger()


def _load_data():
    """
    Загружает данные и делит на тренировочную и тестовую выборку
    """
    logger.info("Старт загрузки данных")
    data = load_iris()
    logger.info("Данные загружены")
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    logger.info("Выборка разбита на train/test")

    return X_train, X_test, y_train, y_test


def train_model(
    model_type: str = "logreg",
    C: float = 1.0,
    n_estimators: int = 100,
) -> dict:
    """
    Запуск обучения модели с логированием в MLflow.

    model_type: тип модели, "logreg" или "rf"
    C: гиперпараметр для логрегрессии
    n_estimators: гиперпараметр для RandomForest

    возвращаем словарь с run_id, метриками и параметрами
    """
    logger.info(
        "Запуск обучения модели. model_type=%s, C=%s, n_estimators=%s",
        model_type,
        C,
        n_estimators,
    )

    X_train, X_test, y_train, y_test = _load_data()

    with mlflow.start_run() as run:
        run_id = run.info.run_id
        logger.info("Создан MLflow run: %s", run_id)

        # логируем тип модели
        mlflow.log_param("model_type", model_type)

        #выбираем и инициализируем модель
        if model_type == "logreg":
            mlflow.log_param("C", C)
            model = LogisticRegression(C=C, max_iter=1000)
            logger.info("Инициализирована модель LogisticRegression (C=%s)", C)
        elif model_type == "rf":
            mlflow.log_param("n_estimators", n_estimators)
            model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
            logger.info(
                "Инициализирована модель RandomForestClassifier (n_estimators=%s)",
                n_estimators,
            )
        else:
            logger.error("Неизвестный тип модели: %s", model_type)
            raise ValueError(f"Unknown model_type: {model_type}")

        #обучение
        logger.info("Начинаю обучение модели")
        model.fit(X_train, y_train)
        logger.info("Обучение модели завершено")

        # метрики
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        logger.info("Accuracy на тесте: %.4f", acc)
        mlflow.log_metric("accuracy", acc)

        # логируем модель в качестве артефакта
        logger.info("Логирую модель в MLflow как артефакт")
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
        )
        logger.info("Модель успешно залогирована. run_id=%s", run_id)

    return {
        "run_id": run_id,
        "metrics": {"accuracy": acc},
        "params": {
            "model_type": model_type,
            "C": C,
            "n_estimators": n_estimators,
        },
    }
