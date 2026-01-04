from src.books.book_repository import BookRepository
from src.books.book_dto import BookDTO, CreateBookDTO, BookDetailDTO, UpdateBookDTO
from src.common.minio_utils import generate_presigned_url, thumb_candidate_keys, upload_file, check_object_exists, delete_object, delete_objects
from src.common.rabbitmq_utils import enqueue_image
from werkzeug.datastructures import FileStorage
import uuid
from typing import List, Dict, Any, Optional

class BookService:
    def __init__(self):
        self.book_repository = BookRepository()

    def get_all_books(self) -> List[BookDTO]:
        books_data = self.book_repository.get_all()
        books_dto = []
        for b in books_data:
            thumb_url = None
            if b.get("image_key"):
                for tkey in thumb_candidate_keys(b["image_key"]):
                    if check_object_exists(tkey):
                        thumb_url = generate_presigned_url(tkey)
                        break
            books_dto.append(BookDTO(id=b['id'], code=b['code'], title=b['title'], author=b['author'], summary=b['summary'], image_key=b['image_key'], thumb_url=thumb_url))
        return books_dto

    def get_book_detail(self, book_id: int) -> Optional[BookDetailDTO]:
        book_data = self.book_repository.get_by_id(book_id)
        if not book_data:
            return None

        book_data["rentals"] = [] # This will be populated by rental_service in the controller

        thumb_url = None
        if book_data.get("image_key"):
            for tkey in thumb_candidate_keys(book_data["image_key"]):
                if check_object_exists(tkey):
                    thumb_url = generate_presigned_url(tkey)
                    break
        book_data["thumb_url"] = thumb_url
        return BookDetailDTO(**book_data)

    def create_book(self, book_data: Dict[str, Any], image_file: Optional[FileStorage]) -> int:
        book_dto = CreateBookDTO(**book_data)
        image_key = None
        if image_file and image_file.filename:
            image_key = f"uploads/{uuid.uuid4().hex}_{image_file.filename.replace(' ', '_')}"
            upload_file(image_file, image_key)

        book_id = self.book_repository.create(book_dto, image_key)

        if image_key:
            enqueue_image(image_key, book_id=book_id)
        
        return book_id

    def update_book(self, book_id: int, book_data: Dict[str, Any], image_file: Optional[FileStorage]):
        book_dto = UpdateBookDTO(**book_data)
        new_image_key = None
        if image_file and image_file.filename:
            new_image_key = f"uploads/{uuid.uuid4().hex}_{image_file.filename.replace(' ', '_')}"
            upload_file(image_file, new_image_key)

        self.book_repository.update(book_id, book_dto, new_image_key)

        if new_image_key:
            enqueue_image(new_image_key, book_id=book_id)

    def delete_book(self, book_id: int):
        book_data = self.book_repository.get_by_id(book_id)
        if not book_data:
            return

        image_key = book_data.get("image_key")

        keys_to_delete = []
        if image_key:
            keys_to_delete.append(image_key)

            keys_to_delete.extend(thumb_candidate_keys(image_key))

        if keys_to_delete:
            delete_objects(keys_to_delete)

        self.book_repository.delete(book_id)
