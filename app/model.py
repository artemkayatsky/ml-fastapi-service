import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self, model_path: str = "model/sentiment_model.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.labels = {0: "Религия", 1: "Наука/Технологии"}
        self._load_model()

    def _load_model(self) -> None:
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Модель не найдена по пути: {self.model_path}")

            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)

            logger.info(f"Модель успешно загружена из {self.model_path}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {e}")
            raise

    def predict_single(self, text: str) -> Dict[str, Any]:
        if self.model is None:
            raise ValueError("Модель не загружена")

        try:
            # Получаем предсказание
            prediction = int(self.model.predict([text])[0])

            # Получаем вероятности
            probabilities = self.model.predict_proba([text])[0]
            confidence = float(probabilities[prediction])

            # Формируем словарь вероятностей
            proba_dict = {
                self.labels[i]: float(prob)
                for i, prob in enumerate(probabilities)
            }

            return {
                "text": text,
                "prediction": prediction,
                "prediction_label": self.labels[prediction],
                "confidence": confidence,
                "probabilities": proba_dict
            }

        except Exception as e:
            logger.error(f"Ошибка при предсказании: {e}")
            raise

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [self.predict_single(text) for text in texts]

    def is_ready(self) -> bool:
        return self.model is not None


# Глобальный экземпляр сервиса
model_service = ModelService()