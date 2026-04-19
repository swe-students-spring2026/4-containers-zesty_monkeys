"""
ML Service API

Exposes transcription functionality via HTTP.
"""

import os
import tempfile
from flask import Flask, request, jsonify

from app.transcriber import load_model, transcribe_audio, extract_words_per_minute
from app.analysis import (
    count_filler_words,
    sentence_length_rating,
    clause_length_rating,
    word_frequency,
    correct_grammar_errors,
)

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
    print("this far")

    try:
        result = transcribe_audio(model, temp_path)
        print("Third check")
        transcript = result["text"]
        segments = result["segments"]
        language = result["language"]

        wpm = extract_words_per_minute(segments)
        filler_words = count_filler_words(transcript)
        sentence_rating = sentence_length_rating(transcript)
        clause_rating = clause_length_rating(transcript)
        freq = word_frequency(transcript, phrase_lengths=[2, 3])
        grammar_errors = correct_grammar_errors(transcript)

        return (
            jsonify(
                {
                    "transcript": transcript,
                    "segments": segments,
                    "language": language,
                    "analysis": {
                        "wpm": wpm,
                        "filler_word_count": filler_words,
                        "sentence_length_rating": sentence_rating,
                        "clause_length_rating": clause_rating,
                        "overused_words": freq["overused_words"],
                        "overused_phrases": freq["overused_phrases"],
                        "grammar_errors": [
                            {
                                "offset": e.error_offset,
                                "length": e.error_length,
                                "message": e.message,
                                "replacements": e.replacements[:3],
                            }
                            for e in grammar_errors
                        ],
                    },
                }
            ),
            200,
        )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
