from src.common.database import db_conn
from src.rentals.rental_dto import CreateRentalDTO
from datetime import date

class RentalRepository:
    def get_by_book_id(self, book_id: int):
        with db_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM rentals WHERE book_id=%s ORDER BY id DESC", (book_id,))
            return cur.fetchall()

    def create(self, book_id: int, rental: CreateRentalDTO) -> int:
        with db_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO rentals (book_id,renter,start_date,status) "
                "VALUES (%s,%s,%s,'OPEN') RETURNING id",
                (book_id, rental.renter, date.today())
            )
            rental_id = cur.fetchone()["id"]
            conn.commit()
            return rental_id

    def return_rental(self, rental_id: int):
        with db_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE rentals SET end_date=%s,status='CLOSED' WHERE id=%s RETURNING book_id",
                (date.today(), rental_id)
            )
            row = cur.fetchone()
            conn.commit()
            return row
