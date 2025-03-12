import os
from typing import Optional
from fastapi import FastAPI, HTTPException 
from fastapi.responses import JSONResponse
from utils.bnnd_wrds_scnnr import BannedWordsScanner
from request_models import ScanRequest, BanWordEdit, Database, NewDatabase
from utils.bnnd_wrds_file_edit import BannedWordsFileEdit

# Завантаження змінних середовища для конфігурації
MODELS = os.getenv("MODELS")
WORDS_DATABASES = os.getenv("WORDS_DATABASES")
TRANSFORMER_NAME = os.getenv("TRANSFORMER_NAME")

DEFAULT_DATABASE = f'{WORDS_DATABASES}/banned_words_basic'





# Ініціалізація FastAPI додатку
app = FastAPI()

try:
    # Створення об'єкта BannedWordsScanner для сканування текстів
    bws = BannedWordsScanner(
        banned_words_file=DEFAULT_DATABASE,  # Шлях до базового файлу зі списком заборонених слів
        model_path=f'{MODELS}/moderation_model.pth',  # Шлях до моделі для модерації
        transformer_name=TRANSFORMER_NAME  # Назва трансформера для моделі
    )
    # Створення об'єкта для редагування списку заборонених слів
    bwfe = BannedWordsFileEdit()
except Exception as e:
    # Обробка помилок при ініціалізації сервісу
    raise RuntimeError({"error": f"Error initialisation service: {str(e)}"})


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},  # Формат помилки у вигляді { "error": "..." }
    )



# Маршрут для сканування тексту на наявність заборонених слів
@app.post("/scan")
async def scan(request: ScanRequest):
    try:
        if not (0 <= request.threshold <= 1):
            raise HTTPException(status_code=422, detail = 'Bad threshold value, must be between [0..1]')

        # Формування шляху до бази даних, якщо вона вказана
        database_path = f"{WORDS_DATABASES}/{request.database_name}" if request.database_name else None
        
        # Перевірка, чи існує база даних
        if request.database_name and not os.path.exists(database_path):
            raise HTTPException(status_code=500, detail = f"Database '{request.database_name}' does not exist!")

        # Якщо вказана база даних, змінюємо її
        if database_path:
            bws.change_words_database(database_path)

        # Виконуємо сканування тексту на заборонені слова
        result = await bws.scan(
            text=request.text, 
            language=request.language,
            return_translation=request.return_translation, 
            threshold=request.threshold
        )
        
        # Повертаємо базу за замовчуванням
        if database_path:
            bws.change_words_database(DEFAULT_DATABASE)
        
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при скануванні тексту
        raise HTTPException(status_code=500, detail=f"Error while scanning text: {str(e)}")

# Маршрут для додавання забороненого слова
@app.post("/add_banword")
async def add_banword(request: BanWordEdit):
    try:
        # Додаємо слова до відповідної бази даних
        if request.database_name:
            result = bwfe.add(f"{WORDS_DATABASES}/{request.database_name}", request.words)
        else:
            result = bwfe.add(DEFAULT_DATABASE, request.words)
            bws.change_words_database(DEFAULT_DATABASE)
        
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при додаванні слова
        raise HTTPException(status_code=500, detail=f"Error while adding words: {str(e)}")

# Маршрут для видалення забороненого слова
@app.post("/remove_banword")
async def remove_banword(request: BanWordEdit):
    try:
        # Видаляємо слово з відповідної бази даних
        if request.database_name:
            result = bwfe.remove(f"{WORDS_DATABASES}/{request.database_name}", request.words)
        else:
            result = bwfe.remove(DEFAULT_DATABASE, request.words)
            bws.change_words_database(DEFAULT_DATABASE)
        
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при видаленні слова
        raise HTTPException(status_code=500, detail=f"Error while deleting words: {str(e)}")
    
# Маршрут для отримання списку заборонених слів
@app.get('/get_banwords')
async def get_banwords(database_name: Optional[str] = None):
    try:
        # Отримуємо список слів із відповідної бази даних
        if database_name:
            if not os.path.exists(f"{WORDS_DATABASES}/{database_name}"):
                raise HTTPException(status_code=500, detail="Database does not exist!")
            else:
                result = bwfe.read_words(f"{WORDS_DATABASES}/{database_name}")
        else:
            result = bwfe.read_words(DEFAULT_DATABASE)
        
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при отриманні списку слів
        raise HTTPException(status_code=500, detail=f"Error while reading words: {str(e)}")