from pydantic import BaseModel

class ScanRequest(BaseModel):
    text: str
    return_translation: bool
    threshold: float

class BanWordEdit(BaseModel):
    words: list