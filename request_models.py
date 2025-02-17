from pydantic import BaseModel

class ScanRequest(BaseModel):
    text: str
    return_translation: bool

class BanWordEdit(BaseModel):
    words: list