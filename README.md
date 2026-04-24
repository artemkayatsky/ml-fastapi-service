# ML Text Classification Service



Микросервис для классификации текстов на основе ML модели, реализованный на FastAPI.



## Описание



Сервис предоставляет REST API для классификации текстов на две категории:

\- \*\*Религия\*\* (класс 0)

\- \*\*Наука/Технологии\*\* (класс 1)



Модель: Logistic Regression с TF-IDF векторизацией, обучена на датасете 20 Newsgroups.



## Быстрый старт



### Предварительные требования



- Docker и Docker Compose

- Python 3.10+ (для локального запуска)



### Запуск с Docker



```bash

\# Клонирование репозитория

git clone <repository-url>

cd ml-fastapi-service



\# Сборка и запуск контейнера

docker-compose up --build



\# Или используя Docker

docker build -t ml-text-classifier .

docker run -p 8000:8000 ml-text-classifier
```

## Примеры запросов

### Предсказание для одного текста

```
{
  "text": "The existence of God cannot be proven by science"
}
```

### Предсказание для нескольких текстов

```
{
  "texts": [
    "Prayer is an important part of spiritual life", "Python is a powerful programming language for data analysis"
  ]
}
```
