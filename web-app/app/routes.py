"""
Defines all HTTP API endpoints for the web application:
- Audio upload and processing pipeline
- Dashboard data retrieval

The main interface between the frontend and backend services.
"""

from flask import Blueprint, jsonify, request
from requests.exceptions import RequestException
from app.services import transcribe_audio

main = Blueprint("main", __name__)


@main.route("/upload", methods=["POST"])
def upload_audio():
    """
    Receives audio file from frontend, sends it to ML service,
    and returns transcription result.
    """
    file = request.files.get("audio")

    if not file:
        return jsonify({"error": "No audio file provided"}), 400

    try:
        transcript = transcribe_audio(file)
    except RequestException as e:
        return jsonify({"error": str(e)}), 500

    return (
        jsonify(
            {
                "transcript": transcript,
            }
        ),
        200,
    )
    # maybe more fields later. talk with frontend and ml-client.


@main.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Retrieves stored speech analysis records.
    """
    return jsonify({"message": "Placeholder!!!"}), 200
