from flask import Blueprint, request, jsonify, send_from_directory
import os
import uuid
from pathlib import Path

bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = Path("/var/lib/sweetbot/uploads")
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

    # Generate a unique filename to avoid collisions
    filename = f"{uuid.uuid4().hex}.png"
    destination = UPLOAD_FOLDER / filename

    file.save(destination)

    return jsonify(
        success=True,
        filename=filename,
        size=destination.stat().st_size
    ), 201

@bp.route("/upload/<uuid>", methods=["GET"])
def get_upload(uuid):

    return send_from_directory(
        UPLOAD_FOLDER,
        f"{uuid}.png",
        mimetype="image/png"
    )
