import os
from typing import Optional
from fastapi import FastAPI, HTTPException
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
    # Обробка помилок при ініціалізації
    raise RuntimeError({"error": f"Error initialisation service: {str(e)}"})

# Маршрут для сканування тексту на наявність заборонених слів
@app.post("/scan")
async def scan(request: ScanRequest):
    try:
        if not (0 <= request.threshold <= 1):
            return {"error": "Bad threshold value, must be between [0..1]"}

        # Перевірка бази даних
        database_path = f"{WORDS_DATABASES}/{request.database_name}" if request.database_name else None
        if request.database_name and not os.path.exists(database_path):
            return {"error": f"Database '{request.database_name}' does not exist!"}

        # Якщо вказана база даних, змінюємо її
        if database_path:
            bws.change_words_database(database_path)

        # Викликається метод сканування з тексту, наданого користувачем
        result = await bws.scan(text=request.text, language=request.language,
                                return_translation=request.return_translation, threshold=request.threshold)
        if database_path:
            bws.change_words_database(DEFAULT_DATABASE)
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при скануванні тексту
        raise HTTPException(status_code=500, detail={"error": f"Error while scanning text: {str(e)}"})

# Маршрут для додавання забороненого слова
@app.post("/add_banword")
async def add_banword(request: BanWordEdit):
    try:
        # Викликається метод додавання слова до списку заборонених слів
        if request.database_name:
            result = bwfe.add(f"{WORDS_DATABASES}/{request.database_name}", request.words)
        else:
            result = bwfe.add(DEFAULT_DATABASE, request.words)
            bws.change_words_database(DEFAULT_DATABASE)
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при додаванні слова
        raise HTTPException(status_code=500, detail={"error": f"Error while adding words: {str(e)}"})

# Маршрут для видалення забороненого слова
@app.post("/remove_banword")
async def remove_banword(request: BanWordEdit):
    try:
        # Викликається метод видалення слова зі списку заборонених
        if request.database_name:
            result = bwfe.remove(f"{WORDS_DATABASES}/{request.database_name}", request.words)
        else:
            result = bwfe.remove(DEFAULT_DATABASE, request.words)
            bws.change_words_database(DEFAULT_DATABASE)
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при видаленні слова
        raise HTTPException(status_code=500, detail={"error": f"Error while deleting words: {str(e)}"})
    
@app.get('/get_banwords')
async def get_banwords(database_name: Optional[str] = None):
    try:
        # Викликається метод виводу всіх слів з бази даних
        if database_name:
            if not os.path.exists(f"{WORDS_DATABASES}/{database_name}"):
                result = {"error": f"Database '{database_name}' does not exist!"}
            else:
                result = bwfe.read_words(f"{WORDS_DATABASES}/{database_name}")
        else:
            result = bwfe.read_words(DEFAULT_DATABASE)
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при виводі всіх слів
        raise HTTPException(status_code=500, detail={"error": f"Error while reading words: {str(e)}"})

@app.post("/create_database")
async def create_database(request: NewDatabase):
    try:
        # Викликається метод створення бази даних
        if os.path.exists(f"{WORDS_DATABASES}/{request.database_name}"):
            result = {"error": f"Database '{request.database_name}' already exist!"}
        else:
            if request.template_database:
                if not os.path.exists(f"{WORDS_DATABASES}/{request.template_database}"):
                    result = {"error": f"Template database '{request.template_database}' does not exist!"}
                else:
                    with open(f"{WORDS_DATABASES}/{request.template_database}", "r") as template_file:
                        template_content = template_file.read()
                    with open(f"{WORDS_DATABASES}/{request.database_name}", "w") as target_file:
                        target_file.write(template_content)
                    result = {"result": f"Database '{request.database_name}' successfully created!"}
            else:
                with open(f"{WORDS_DATABASES}/{request.database_name}", "w") as f:
                    pass
                result = {"result": f"Database '{request.database_name}' successfully created!"}
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при створенні бази даних
        raise HTTPException(status_code=500, detail={"error": f"Error while creating database: {str(e)}"})

@app.post("/delete_database")
async def delete_database(request: Database):
    try:
        # Викликається метод видалення бази даних
        if f"{WORDS_DATABASES}/{request.database_name}" == DEFAULT_DATABASE:
            result = {"error": f"Could not delete default database!"}
        elif not os.path.exists(f"{WORDS_DATABASES}/{request.database_name}"):  # Перевіряємо, чи існує файл
            result = {"error": f"Database '{request.database_name}' does not exist!"}  # Повернення результату клієнту
        else:
            os.remove(f"{WORDS_DATABASES}/{request.database_name}")
            result = {"result": f"Database '{request.database_name}' successfully deleted!"}  # Повернення результату клієнту
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при видаленні бази даних
        raise HTTPException(status_code=500, detail={"error": f"Error while deleting database: {str(e)}"})

@app.get("/get_databases")
async def get_databases():
    try:
        # Викликається метод виводу всіх баз даних
        result = {"databases": os.listdir(WORDS_DATABASES)}
        print(result)  # Виведення результату в консоль для налагодження
        return result  # Повернення результату клієнту
    except Exception as e:
        # Обробка помилок при виводі всіх слів
        raise HTTPException(status_code=500, detail={"error": f"Error while listing databases: {str(e)}"})
