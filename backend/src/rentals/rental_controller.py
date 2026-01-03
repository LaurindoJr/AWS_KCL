from flask import Blueprint, request, jsonify
from flasgger import swag_from
from src.rentals.rental_service import RentalService
from src.common.audit import log_audit # Import the moved log_audit

rental_bp = Blueprint('rentals', __name__)
rental_service = RentalService()

@rental_bp.route("/api/books/<int:book_id>/rentals", methods=["POST"]) # ID is now integer
@swag_from({
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'integer', # ID is now integer
            'required': True
        },
        {
            'name': 'renter',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'renter': {'type': 'string'}
                },
                'required': ['renter']
            }
        }
    ],
    'responses': {
        201: {'description': 'Rental created successfully'},
        400: {'description': 'Invalid input'}
    }
})
def rent_book(book_id: int): # ID is now integer
    data = request.json
    if not data or "renter" not in data:
        return jsonify({"error": "Renter name is required"}), 400

    renter = data["renter"].strip()
    if not renter:
        return jsonify({"error": "Renter name cannot be empty"}), 400

    try:
        rental_id = rental_service.create_rental(book_id, {"renter": renter})
        log_audit("RENT", {"book_id": book_id, "renter": renter, "rental_id": rental_id})
        return jsonify({"message": "Rental created successfully", "rental_id": rental_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rental_bp.route("/api/rentals/<int:rental_id>/return", methods=["PUT"]) # ID is now integer
@swag_from({
    'parameters': [
        {
            'name': 'rental_id',
            'in': 'path',
            'type': 'integer', # ID is now integer
            'required': True
        }
    ],
    'responses': {
        200: {'description': 'Rental returned successfully'},
        404: {'description': 'Rental not found'}
    }
})
def return_rental(rental_id: int): # ID is now integer
    try:
        result = rental_service.return_rental(rental_id)
        if not result:
            return jsonify({"error": "Rental not found"}), 404
        log_audit("RETURN", {"rental_id": rental_id, "book_id": result["book_id"]})
        return jsonify({"message": "Rental returned successfully", "book_id": result["book_id"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
