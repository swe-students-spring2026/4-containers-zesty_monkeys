"""
ML Service API

Exposes transcription functionality via HTTP.
"""

import os
import tempfile
from flask import Flask, request, jsonify

from app.transcriber import load_model, transcribe_audio

app = Flask(__name__)

model = load_model("base")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """
    Accepts audio file from backend, saves it temporarily,
    transcribes it using the loaded Whisper model,
    and returns transcription.
    """
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        file.save(tmp.name)
        temp_path = tmp.name

    try:
        result = transcribe_audio(model, temp_path)
        return (
            jsonify(
                {
                    "transcript": result["text"],
                    "segments": result["segments"],
                    "language": result["language"],
                }
            ),
            200,
        )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
