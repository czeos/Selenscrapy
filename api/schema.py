from pydantic import BaseModel

class APOCTest(BaseModel):
    name: str
    id: int