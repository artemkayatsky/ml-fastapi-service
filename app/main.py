from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from typing import Dict, Any

from app.schemas import (
    TextInput,
    BatchTextInput,
    PredictionResponse,
    BatchPredictionResponse,
    HealthResponse
)
from app.model import model_service
from app.utils import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title="ML Text Classification Service",
    description="Микросервис для классификации текстов на основе ML модели",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()

    logger.info(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("startup")
async def startup_event():
    logger.info("Запуск ML сервиса...")
    if model_service.is_ready():
        logger.info("Модель успешно загружена и готова к работе")
    else:
        logger.error("Модель не загружена!")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Остановка ML сервиса...")


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "ML Text Classification Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "predict_batch": "/predict/batch",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    try:
        model_ready = model_service.is_ready()
        return HealthResponse(
            status="OK" if model_ready else "ERROR",
            model_loaded=model_ready,
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="ERROR",
            model_loaded=False,
            version="1.0.0"
        )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Prediction"],
    summary="Предсказание для одного текста",
    description="Принимает текст и возвращает классификацию с вероятностями"
)
async def predict(input_data: TextInput):
    try:
        logger.info(f"Predict request received, text length: {len(input_data.text)}")

        result = model_service.predict_single(input_data.text)

        logger.info(
            f"Prediction: {result['prediction_label']} "
            f"(confidence: {result['confidence']:.3f})"
        )

        return PredictionResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при выполнении предсказания"
        )


@app.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    tags=["Prediction"],
    summary="Пакетное предсказание",
    description="Принимает список текстов и возвращает классификацию для каждого"
)
async def predict_batch(input_data: BatchTextInput):
    try:
        logger.info(f"Batch predict request received, texts count: {len(input_data.texts)}")

        results = model_service.predict_batch(input_data.texts)

        logger.info(f"Batch prediction completed for {len(results)} texts")

        return BatchPredictionResponse(
            predictions=[PredictionResponse(**r) for r in results]
        )

    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при выполнении пакетного предсказания"
        )


@app.get("/model/info", tags=["Model"])
async def model_info():
    return {
        "model_type": "Logistic Regression with TF-IDF",
        "labels": model_service.labels,
        "model_loaded": model_service.is_ready()
    }


# Обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера"}
    )