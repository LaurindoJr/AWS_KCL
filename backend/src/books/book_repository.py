from src.common.database import db_conn
from src.books.book_dto import CreateBookDTO, UpdateBookDTO
from typing import Optional

class BookRepository:
    def get_all(self):
        with db_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM books ORDER BY id DESC")
            return cur.fetchall()

    def get_by_id(self, book_id: int):
        with db_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM books WHERE id=%s", (book_id,))
            return cur.fetchone()

    def create(self, book: CreateBookDTO, image_key: Optional[str]) -> int:
        with db_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO books (code,title,author,summary,image_key) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (book.code, book.title, book.author, book.summary, image_key),
            )
            book_id = cur.fetchone()["id"]
            conn.commit()
            return book_id

    def update(self, book_id: int, book: UpdateBookDTO, image_key: Optional[str]):
        with db_conn() as conn, conn.cursor() as cur:
            if image_key:
                cur.execute(
                    "UPDATE books SET title=%s,author=%s,summary=%s,image_key=%s WHERE id=%s",
                    (book.title, book.author, book.summary, image_key, book_id)
                )
            else:
                cur.execute(
                    "UPDATE books SET title=%s,author=%s,summary=%s WHERE id=%s",
                    (book.title, book.author, book.summary, book_id)
                )
            conn.commit()

    def delete(self, book_id: int):
        with db_conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
            conn.commit()
