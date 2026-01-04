import json
from datetime import date

from flask import Flask, jsonify
from flasgger import Swagger
from werkzeug.exceptions import HTTPException
import logging

from src.books.book_controller import book_bp
from src.rentals.rental_controller import rental_bp
from src.common.minio_utils import init_minio_bucket


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder = CustomJsonEncoder
swagger = Swagger(app)

# Register blueprints
app.register_blueprint(book_bp)
app.register_blueprint(rental_bp)

@app.route("/health")
def health():
    return jsonify({"ok": True}), 200

init_minio_bucket()

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e

    app.logger.error("An unhandled exception occurred:", exc_info=True)
    return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
