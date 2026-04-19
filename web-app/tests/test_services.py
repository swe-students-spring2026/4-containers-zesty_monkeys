"""
This file is for testing app/services.py.
"""

# pylint: disable=too-few-public-methods, missing-docstring, unnecessary-lambda
import pytest
import requests
from app.services import (
    transcribe_audio,
    get_user_by_username,
    add_entry,
    create_user,
    get_user_by_id,
)


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

    monkeypatch.setattr("app.services.add_entry", lambda _: None)

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
        return MockResponse({})  # no transcript

    monkeypatch.setattr("app.services.requests.post", mock_post)

    monkeypatch.setattr("app.services.add_entry", lambda _: None)

    file = MockFile()
    result = transcribe_audio(file)

    assert result == ""


def test_get_user_by_username_found(monkeypatch):
    """
    Test retrieving user by username.
    """

    class MockCollection:
        """
        Mock collection with find_one method.
        """

        def find_one(self, __):
            """
            Return mock user document if username matches.
            """
            return {"_id": "123", "username": "test", "password": "pw", "entries": []}

    class MockDB:
        """
        Mock database with users collection.
        """

        users = MockCollection()

    monkeypatch.setattr("app.services.get_db", lambda: MockDB())

    user = get_user_by_username("test")

    assert user is not None
    assert user.username == "test"


def test_get_user_by_username_not_found(monkeypatch):
    """
    Test retrieving non-existing user.
    """

    class MockCollection:
        """
        Mock collection with find_one method that returns None.
        """

        def find_one(self, __):
            """
            Simulate user not found.
            """
            return None

    class MockDB:
        """
        Mock database with users collection.
        """

        users = MockCollection()

    monkeypatch.setattr("app.services.get_db", lambda: MockDB())

    user = get_user_by_username("ghost")

    assert user is None


def test_get_user_by_id_success(monkeypatch):
    """
    Test retrieving user by ID.
    """

    class MockUsers:
        def find_one(self, _):
            return {
                "_id": "507f1f77bcf86cd799439011",
                # arbitrary ObjectID string
                "username": "test",
                "password": "pw",
                "entries": [],
            }

    class MockDB:
        users = MockUsers()

    monkeypatch.setattr("app.services.get_db", lambda: MockDB())

    user = get_user_by_id("507f1f77bcf86cd799439011")

    assert user is not None
    assert user.username == "test"


def test_create_user_success(monkeypatch):
    """
    Test creating a new user.
    """

    class MockEntries:
        def insert_one(self, _):
            return type("obj", (), {"inserted_id": "entries_id"})

    class MockUsers:
        def __init__(self):
            self.called = False

        def find_one(self, __):
            if not self.called:
                self.called = True
                return None
            return {
                "_id": "user_id",
                "username": "new_user",
                "password": "pw",
                "entries": "entries_id",
            }

        def insert_one(self, __):
            return type("obj", (), {"inserted_id": "user_id"})

    class MockDB:
        users = MockUsers()
        entries = MockEntries()

    monkeypatch.setattr("app.services.get_db", lambda: MockDB())

    user = create_user("new_user", "pw")

    assert user.username == "new_user"


def test_create_user_duplicate(monkeypatch):
    """
    Test creating a user with existing username.
    """

    class MockUsers:
        def find_one(self, __):
            return {"username": "existing"}

    class MockDB:
        users = MockUsers()

    monkeypatch.setattr("app.services.get_db", lambda: MockDB())

    with pytest.raises(ValueError):
        create_user("existing", "pw")


def test_add_entry_success(monkeypatch):
    """
    Test adding entry for authenticated user.
    """

    class MockUser:
        is_authenticated = True
        username = "test_user"

    class MockUsers:
        def find_one(self, __):
            return {"entries": "entries_id"}

    class MockEntries:
        def __init__(self):
            self.updated = False

        def update_one(self, __, ___):
            self.updated = True

    class MockDB:
        users = MockUsers()
        entries = MockEntries()

    monkeypatch.setattr("app.services.get_db", lambda: MockDB())
    monkeypatch.setattr("app.services.current_user", MockUser())

    add_entry({"transcript": "hello"})


def test_add_entry_not_logged_in(monkeypatch):
    """
    Test add_entry raises error when user not logged in.
    """

    class MockUser:
        is_authenticated = False

    monkeypatch.setattr("app.services.current_user", MockUser())
    monkeypatch.setattr("app.services.get_db", lambda: None)

    with pytest.raises(ValueError):
        add_entry({"transcript": "hello"})
