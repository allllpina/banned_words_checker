import os
from fastapi import FastAPI, HTTPException
from utils.bnnd_wrds_scnnr import BannedWordsScanner
from request_models import ScanRequest, BanWordEdit
from utils.bnnd_wrds_file_edit import BannedWordsFileEdit

# Завантаження змінних середовища
MODELS = os.getenv("MODELS")
WORDS_DATABASES = os.getenv("WORDS_DATABASES")
TRANSFORMER_NAME = os.getenv("TRANSFORMER_NAME")

app = FastAPI()

try:
    bws = BannedWordsScanner(
        banned_words_file=f'{WORDS_DATABASES}/banned_words.txt',
        model_path=f'{MODELS}/moderation_model.pth',
        transformer_name=TRANSFORMER_NAME
    )
    bwfe = BannedWordsFileEdit(banned_words_file=f'{WORDS_DATABASES}/banned_words.txt')
except Exception as e:
    raise RuntimeError(f"Помилка ініціалізації сервісу: {str(e)}")


@app.post("/scan")
async def scan(request: ScanRequest):
    try:
        result = await bws.scan(request.text)
        print(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка під час сканування тексту: {str(e)}")


@app.post("/add_banword")
async def add_banword(request: BanWordEdit):
    try:
        result = bwfe.add(request.words, bws)
        print(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка під час додавання слова: {str(e)}")


@app.post("/remove_banword")
async def remove_banword(request: BanWordEdit):
    try:
        result = bwfe.remove(request.words, bws)
        print(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка під час видалення слова: {str(e)}")
