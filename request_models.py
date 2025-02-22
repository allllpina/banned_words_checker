from pydantic import BaseModel
from typing import Optional

class ScanRequest(BaseModel):
    text: str
    language: Optional[str] = 'auto'
    return_translation: Optional[bool] = False
    threshold: Optional[float] = 0.5
    database_name: Optional[str] = None

class BanWordEdit(BaseModel):
    words: list
    database_name: Optional[str] = None

class Database(BaseModel):
    database_name: str
