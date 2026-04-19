"""
Tests for server.py in ml client.
"""

# pylint: disable=redefined-outer-name

import io
import pytest
from app.server import app


@pytest.fixture
def flask_client():
    """
    Provides a Flask test client for testing server endpoints.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_transcribe_success(monkeypatch, flask_client):
    """
    Test /transcribe endpoint returns expected JSON response.
    """

    def mock_transcribe(_, __):  # model and path args are ignored whatever.
        return {"text": "hello world", "segments": [], "language": "en"}

    monkeypatch.setattr("app.server.transcribe_audio", mock_transcribe)

    data = {"file": (io.BytesIO(b"fake audio"), "test.wav")}

    response = flask_client.post(
        "/transcribe", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    json_data = response.get_json()

    assert json_data["transcript"] == "hello world"
    assert json_data["language"] == "en"


def test_transcribe_no_file(flask_client):
    """
    Test /transcribe endpoint when no file is provided.
    """

    response = flask_client.post("/transcribe", data={})

    assert response.status_code == 400
    assert "error" in response.get_json()
