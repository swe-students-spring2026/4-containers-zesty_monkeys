"""
This file is for testing app/services.py.
"""
import pytest
import requests
from app.services import transcribe_audio

class MockResponse:
    """
    Mock response object to simulate requests.post return value.
    """
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
        self.ok = status_code == 200

    def json(self):
        """
        Return mock json data.
        """
        return self._json


class MockFile:
    """
    Mock FileStorage-like object.
    """
    filename = "test.wav"
    mimetype = "audio/wav"

    @property
    def stream(self):
        """
        Simulate file stream containing audio bytes.
        """
        return b"fake-audio-bytes"


def test_transcribe_audio_success(monkeypatch):
    """
    Test successful transcription from ML service.
    """

    def mock_post(*_, **__):
        return MockResponse({"transcript": "hello world"})

    # IMPORTANT: patch the correct import path
    monkeypatch.setattr("app.services.requests.post", mock_post)

    file = MockFile()
    result = transcribe_audio(file)

    assert result == "hello world"


def test_transcribe_audio_connection_error(monkeypatch):
    """
    Test failure when ML service is unreachable.
    """

    def mock_post(*_, **__):
        raise requests.exceptions.RequestException("Connection failed")

    monkeypatch.setattr("app.services.requests.post", mock_post)

    file = MockFile()

    with pytest.raises(Exception):
        transcribe_audio(file)


def test_transcribe_audio_missing_transcript(monkeypatch):
    """
    Test response without transcript field.
    """

    def mock_post(*_, **__):
        return MockResponse({}) # no transcript

    monkeypatch.setattr("app.services.requests.post", mock_post)

    file = MockFile()
    result = transcribe_audio(file)

    assert result == ""
