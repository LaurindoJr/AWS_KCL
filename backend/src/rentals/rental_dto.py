from pydantic import BaseModel
from datetime import date
from typing import Optional

class RentalDTO(BaseModel):
    id: int
    book_id: int
    renter: str
    start_date: date
    end_date: Optional[date] = None
    status: str

class CreateRentalDTO(BaseModel):
    renter: str
