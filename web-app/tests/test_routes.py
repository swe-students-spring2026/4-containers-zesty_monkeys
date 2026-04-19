"""
This file is for testing app/routes.py.
"""

import io
from app import create_app


def test_upload_audio_route(monkeypatch):
    """
    Test /upload endpoint with mocked transcription service.
    """

    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    # mock transcribe_audio
    def mock_transcribe(_):
        return "hello world"

    monkeypatch.setattr("app.routes.transcribe_audio", mock_transcribe)

    data = {"audio": (io.BytesIO(b"fake audio"), "test.wav")}

    response = client.post("/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.json["transcript"] == "hello world"
