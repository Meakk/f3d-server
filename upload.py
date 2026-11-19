from flask import Blueprint, request, jsonify, send_from_directory
import hashlib
import os
from pathlib import Path

bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = Path(os.getenv('UPLOAD_FOLDER'))
UPLOAD_TOKEN = os.getenv('UPLOAD_TOKEN')

@bp.route('/upload', methods=['POST'])
def upload():
    token = request.headers.get('Authorization')
    if token != f"Bearer {UPLOAD_TOKEN}":
        return jsonify(error="Unauthorized"), 401

    if "file" not in request.files:
        return jsonify(error="Missing file field"), 400

    file = request.files["file"]

    # Check PNG signature
    if file.read(8) != b"\x89PNG\r\n\x1a\n":
        return jsonify(error="Only PNG files are accepted"), 400

    file.seek(0)

    # Name the file after its content hash, so identical uploads share a single file
    digest = hashlib.sha256()
    while chunk := file.read(65536):
        digest.update(chunk)
    file.seek(0)

    filename = f"{digest.hexdigest()}.png"
    destination = UPLOAD_FOLDER / filename

    created = not destination.exists()
    if created:
        file.save(destination)

    return jsonify(
        success=True,
        sha256=digest.hexdigest(),
        size=destination.stat().st_size
    ), 201 if created else 200

@bp.route("/upload/<file_hash>", methods=["GET"])
def get_upload(file_hash):

    return send_from_directory(
        UPLOAD_FOLDER,
        f"{file_hash}.png",
        mimetype="image/png"
    )
