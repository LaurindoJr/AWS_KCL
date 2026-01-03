from src.rentals.rental_repository import RentalRepository
from src.rentals.rental_dto import RentalDTO, CreateRentalDTO
from typing import List, Dict, Any, Optional

class RentalService:
    def __init__(self):
        self.rental_repository = RentalRepository()

    def get_rentals_by_book_id(self, book_id: int) -> List[RentalDTO]:
        rentals_data = self.rental_repository.get_by_book_id(book_id)
        return [RentalDTO(**r) for r in rentals_data]

    def create_rental(self, book_id: int, rental_data: Dict[str, Any]) -> int:
        rental_dto = CreateRentalDTO(**rental_data)
        rental_id = self.rental_repository.create(book_id, rental_dto)
        return rental_id

    def return_rental(self, rental_id: int) -> Optional[Dict[str, Any]]:
        row = self.rental_repository.return_rental(rental_id)
        if row:
            return {"book_id": row["book_id"], "end_date": row["end_date"]}
        return None
