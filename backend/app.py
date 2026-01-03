import json
from datetime import date

from flask import Flask, jsonify
from flasgger import Swagger
from werkzeug.exceptions import HTTPException
import logging

from src.books.book_controller import book_bp
from src.rentals.rental_controller import rental_bp
from src.common.minio_utils import init_minio_bucket


# Aplicação
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

# Initialize MinIO bucket
init_minio_bucket()

@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # Log every non-HTTP exception and return a generic 500, or a specific error message.
    app.logger.error("An unhandled exception occurred:", exc_info=True)
    return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == "__main__":
    # Example of how to create tables, usually handled by migrations
    # with db_conn() as conn, conn.cursor() as cur:
    #     cur.execute("CREATE TABLE IF NOT EXISTS books (id SERIAL PRIMARY KEY, title VARCHAR(255));")
    #     conn.commit()
    app.run(host="0.0.0.0", port=5000)
