from fastapi import FastAPI
from pydantic import BaseModel, Field
import os
import mlflow
from mlflow.tracking import MlflowClient

from .train import train_model
from .logger import get_logger

logger = get_logger()

app = FastAPI(title="MLflow HW2")

tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(tracking_uri)
client = MlflowClient(tracking_uri=tracking_uri)

SUPPORTED_MODELS = ["logreg", "rf"]


class RunRequest(BaseModel):
    model_type: str = Field(
        "logreg",
        description="Тип модели: 'logreg' или 'rf'",
    )
    C: float = Field(
        1.0,
        description="Гиперпараметр для логрегрессии (игнорируется для rf)",
    )
    n_estimators: int = Field(
        100,
        description="Число деревьев для RandomForest (игнорируется для logreg)",
    )


@app.get("/health")
def health():
    logger.info("запрос /health")
    return {"status": "ok"}


@app.get("/models/available")
def list_available_models():
    """
    возвращает список доступных моделей
    """
    logger.info("запрос /models/available")
    return {"models": SUPPORTED_MODELS}


@app.post("/experiments/run")
def run_experiment(req: RunRequest):
    """

    запускает обучение модели и логирует всё в MLflow.
    """
    logger.info(
        "запрос /experiments/run: model_type=%s, C=%s, n_estimators=%s",
        req.model_type,
        req.C,
        req.n_estimators,
    )

    if req.model_type not in SUPPORTED_MODELS:
        logger.warning("неподдерживаемый тип модели: %s", req.model_type)
        return {
            "status": "error",
            "message": f"Unsupported model_type: {req.model_type}",
            "supported_models": SUPPORTED_MODELS,
        }

    result = train_model(
        model_type=req.model_type,
        C=req.C,
        n_estimators=req.n_estimators,
    )

    logger.info("эксперимет выполнен успушно. run_id=%s", result["run_id"])

    return {
        "status": "finished",
        "run_id": result["run_id"],
        "metrics": result["metrics"],
        "params": result["params"],
    }


@app.get("/experiments/{run_id}")
def get_experiment_info(run_id: str):
    
    """
    возвращает информацию по эксперименту из mlflow
    
    """

    logger.info("запрос /experiments/%s", run_id)
    run = client.get_run(run_id)
    artifacts = [a.path for a in client.list_artifacts(run_id, "model")]
    logger.info(
        "инфа по эксперименту взята. run_id=%s, status=%s",
        run_id,
        run.info.status,
    )
    return {
        "run_id": run.info.run_id,
        "status": run.info.status,
        "params": run.data.params,
        "metrics": run.data.metrics,
        "artifacts": artifacts,
    }


@app.get("/models/{run_id}")
def get_model_info(run_id: str):
    """
    возвращает URI модели для mlflow.sklearn.load_model.
    """
    logger.info("запрос /models/%s", run_id)
    model_uri = f"runs:/{run_id}/model"
    logger.info("сформирован model_uri=%s для run_id=%s", model_uri, run_id)
    return {
        "run_id": run_id,
        "model_uri": model_uri,
    }
