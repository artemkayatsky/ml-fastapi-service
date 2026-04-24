from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class TextInput(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Текст для классификации"
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Текст не может быть пустым')
        return v.strip()


class BatchTextInput(BaseModel):
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Список текстов для классификации"
    )

    @field_validator('texts')
    @classmethod
    def validate_texts(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('Список текстов не может быть пустым')
        return [text.strip() for text in v if text and text.strip()]


class PredictionResponse(BaseModel):
    text: str
    prediction: int
    prediction_label: str
    confidence: float
    probabilities: dict


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str