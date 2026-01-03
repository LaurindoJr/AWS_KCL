from pydantic import BaseModel
from typing import Optional, List

class BookDTO(BaseModel):
    id: int
    code: str
    title: str
    author: str
    summary: Optional[str] = None
    image_key: Optional[str] = None
    thumb_url: Optional[str] = None

class CreateBookDTO(BaseModel):
    code: str
    title: str
    author: str
    summary: Optional[str] = None

class UpdateBookDTO(BaseModel):
    title: str
    author: str
    summary: Optional[str] = None

class BookDetailDTO(BookDTO):
    rentals: List = []
