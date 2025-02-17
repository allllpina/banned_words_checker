import os
from fastapi import FastAPI, HTTPException
from utils.bnnd_wrds_scnnr import BannedWordsScanner
from request_models import ScanRequest, BanWordEdit
from utils.bnnd_wrds_file_edit import BannedWordsFileEdit

# Завантаження змінних середовища для конфігурації
MODELS = os.getenv("MODELS")
WORDS_DATABASES = os.getenv("WORDS_DATABASES")
TRANSFORMER_NAME = os.getenv("TRANSFORMER_NAME")

# Ініціалізація FastAPI додатку
app = FastAPI()

try:
    # Створення об'єкта BannedWordsScanner для сканування текстів
    bws = BannedWordsScanner(
        banned_words_file=f'{WORDS_DATABASES}/banned_words.txt',  # Шлях до файлу зі списком заборонених слів
        model_path=f'{MODELS}/moderation_model.pth',  # Шлях до моделі для модерації
        transformer_name=TRANSFORMER_NAME  # Назва трансформера для моделі
    )
    # Створення об'єкта для редагування списку заборонених слів
    bwfe = BannedWordsFileEdit(banned_words_file=f'{WORDS_DATABASES}/banned_words.txt')
except Exception as e:
    # Обробка помилок при ініціалізації
    raise RuntimeError(f"Помилка ініціалізації сервісу: {str(e)}")

# Маршрут для сканування тексту на наявність заборонених слів
@app.post("/scan")
async def scan(request: ScanRequest):
    try:
        if request.threshold > 1 or request.threshold < 0:
            return {"Помилка у пороговому значенні, воно має бути в межах від 0 до 1"}
        # Викликається метод сканування з тексту, наданого користувачем
        result = await bws.scan(request.text, return_translation = request.return_translation, threshold=request.threshold)
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при скануванні тексту
        raise HTTPException(status_code=500, detail=f"Помилка під час сканування тексту: {str(e)}")

# Маршрут для додавання забороненого слова
@app.post("/add_banword")
async def add_banword(request: BanWordEdit):
    try:
        # Викликається метод додавання слова до списку заборонених слів
        result = bwfe.add(request.words, bws)
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при додаванні слова
        raise HTTPException(status_code=500, detail=f"Помилка під час додавання слова: {str(e)}")

# Маршрут для видалення забороненого слова
@app.post("/remove_banword")
async def remove_banword(request: BanWordEdit):
    try:
        # Викликається метод видалення слова зі списку заборонених
        result = bwfe.remove(request.words, bws)
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при видаленні слова
        raise HTTPException(status_code=500, detail=f"Помилка під час видалення слова: {str(e)}")
    
@app.get('/get_banwords')
async def get_banwords():
    try:
        result = bwfe.read_words()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка під час  читання списку слів: {str(e)}")
