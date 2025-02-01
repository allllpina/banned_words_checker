from pydantic import BaseModel

class ScanRequest(BaseModel):
    text: str

class BanWordEdit(BaseModel):
    words: list