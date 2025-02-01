FROM python:3.12.3

WORKDIR /app

# Копіюємо файли з локального репозиторію в контейнер
COPY . /app

# Встановлення залежностей з requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо .env файл в контейнер
COPY .env /app/.env

# Встановлення змінних середовища для шляхи моделей
ENV MODELS=/app/materials/models
ENV WORDS_DATABASES=/app/materials/words_databases
ENV TRANSFORMER_NAME='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

# Відкриття порту, на якому працюватиме FastAPI
EXPOSE 8000

# Команда для запуску FastAPI за допомогою uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]