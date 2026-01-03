from flask import Blueprint, request, jsonify
from flasgger import swag_from
from src.books.book_service import BookService
from src.rentals.rental_service import RentalService # Need for populating rentals in get_book_detail
from src.common.audit import log_audit # Import the moved log_audit

book_bp = Blueprint('books', __name__)
book_service = BookService()
rental_service = RentalService() # Instance of RentalService to fetch rentals

@book_bp.route("/api/books", methods=["GET"])
@swag_from({
    'responses': {
        200: {
            'description': 'A list of books',
            'schema': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/BookDTO'
                }
            }
        }
    },
    'definitions': {
        'BookDTO': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'}, # ID is now integer
                'code': {'type': 'string'},
                'title': {'type': 'string'},
                'author': {'type': 'string'},
                'summary': {'type': 'string'},
                'image_key': {'type': 'string'},
                'thumb_url': {'type': 'string'},
            }
        }
    }
})
def get_books():
    books = book_service.get_all_books()
    return jsonify([book.dict() for book in books])

@book_bp.route("/api/books", methods=["POST"])
@swag_from({
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'code',
            'in': 'formData',
            'type': 'string',
            'required': True
        },
        {
            'name': 'title',
            'in': 'formData',
            'type': 'string',
            'required': True
        },
        {
            'name': 'author',
            'in': 'formData',
            'type': 'string',
            'required': True
        },
        {
            'name': 'summary',
            'in': 'formData',
            'type': 'string'
        },
        {
            'name': 'image',
            'in': 'formData',
            'type': 'file'
        }
    ],
    'responses': {
        201: {'description': 'Book created successfully'},
        400: {'description': 'Invalid input'}
    }
})
def create_book():
    data = request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    code = data.get("code", "").strip()
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    summary = data.get("summary", "").strip()

    if not all([code, title, author]):
        return jsonify({"error": "Code, title, and author are required"}), 400
    
    book_data = {
        "code": code,
        "title": title,
        "author": author,
        "summary": summary
    }
    image_file = request.files.get("image")

    book_id = book_service.create_book(book_data, image_file)
    log_audit("CREATE", {"book_id": book_id, "code": code})
    return jsonify({"message": "Book created successfully", "book_id": book_id}), 201


@book_bp.route("/api/books/<int:book_id>", methods=["GET"]) # ID is now integer
@swag_from({
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'integer', # ID is now integer
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': 'A single book',
            'schema': {
                '$ref': '#/definitions/BookDetailDTO'
            }
        },
        404: {'description': 'Book not found'}
    },
    'definitions': {
        'BookDetailDTO': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'}, # ID is now integer
                'code': {'type': 'string'},
                'title': {'type': 'string'},
                'author': {'type': 'string'},
                'summary': {'type': 'string'},
                'image_key': {'type': 'string'},
                'thumb_url': {'type': 'string'},
                'rentals': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/RentalDTO'
                    }
                }
            }
        },
        'RentalDTO': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'}, # ID is now integer
                'book_id': {'type': 'integer'}, # ID is now integer
                'renter': {'type': 'string'},
                'start_date': {'type': 'string', 'format': 'date'},
                'end_date': {'type': 'string', 'format': 'date'},
                'status': {'type': 'string'}
            }
        }
    }
})
def get_book(book_id: int): # ID is now integer
    book = book_service.get_book_detail(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    rentals = rental_service.get_rentals_by_book_id(book_id)
    book.rentals = [rental.dict() for rental in rentals]

    return jsonify(book.dict())

@book_bp.route("/api/books/<int:book_id>", methods=["PUT"]) # ID is now integer
@swag_from({
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'integer', # ID is now integer
            'required': True
        },
        {
            'name': 'title',
            'in': 'formData',
            'type': 'string',
            'required': True
        },
        {
            'name': 'author',
            'in': 'formData',
            'type': 'string',
            'required': True
        },
        {
            'name': 'summary',
            'in': 'formData',
            'type': 'string'
        },
        {
            'name': 'image',
            'in': 'formData',
            'type': 'file'
        }
    ],
    'responses': {
        200: {'description': 'Book updated successfully'},
        400: {'description': 'Invalid input'}
    }
})
def update_book(book_id: int): # ID is now integer
    data = request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    summary = data.get("summary", "").strip()

    if not all([title, author]):
        return jsonify({"error": "Title and author are required"}), 400

    book_data = {
        "title": title,
        "author": author,
        "summary": summary
    }
    image_file = request.files.get("image")

    try:
        book_service.update_book(book_id, book_data, image_file)
        log_audit("UPDATE", {"book_id": book_id})
        return jsonify({"message": "Book updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@book_bp.route("/api/books/<int:book_id>", methods=["DELETE"]) # ID is now integer
@swag_from({
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'integer', # ID is now integer
            'required': True
        }
    ],
    'responses': {
        200: {'description': 'Book deleted successfully'},
        500: {'description': 'Failed to delete book'}
    }
})
def delete_book(book_id: int): # ID is now integer
    try:
        book_service.delete_book(book_id)
        log_audit("DELETE", {"book_id": book_id})
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
