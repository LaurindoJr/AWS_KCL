import os
from src.rentals.rental_repository_postgres import RentalRepository as PgRepo
from src.rentals.rental_repository_dynamo import RentalRepositoryDynamo as DdbRepo
from src.common.dynamo_health import dynamo_rentals_available

MODE = os.getenv("RENTALS_STORE", "auto").lower()  # postgres | dynamo | auto

class RentalRepositoryRouter:
    def __init__(self):
        self.pg = PgRepo()
        self.ddb = DdbRepo()

    def _use_ddb(self) -> bool:
        if MODE == "postgres":
            return False
        if MODE == "dynamo":
            return True
        # auto:
        return dynamo_rentals_available()

    def get_by_book_id(self, book_id: int):
        if self._use_ddb():
            try:
                return self.ddb.get_by_book_id(book_id)
            except Exception as e:
                print(f"[rentals] erro no dynamo get_by_book_id -> fallback pg: {e}")
                return self.pg.get_by_book_id(book_id)
        return self.pg.get_by_book_id(book_id)

    def create(self, book_id: int, rental):
        if self._use_ddb():
            try:
                rental_id = self.ddb.create(book_id, rental)
                # cria lookup
                self.ddb.create_lookup(book_id, rental_id)
                return rental_id
            except Exception as e:
                print(f"[rentals] erro no dynamo create -> fallback pg: {e}")
                return self.pg.create(book_id, rental)
        return self.pg.create(book_id, rental)

    def return_rental(self, rental_id: int):
        if self._use_ddb():
            try:
                return self.ddb.return_rental(rental_id)
            except Exception as e:
                print(f"[rentals] erro no dynamo return_rental -> fallback pg: {e}")
                return self.pg.return_rental(rental_id)
        return self.pg.return_rental(rental_id)
