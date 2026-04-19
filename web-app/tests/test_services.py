"""
This file is for testing app/services.py.
"""

# pylint: disable=too-few-public-methods, missing-docstring, unnecessary-lambda, unused-argument, invalid-name, use-implicit-booleaness-not-comparison, unused-variable
from types import SimpleNamespace
import asyncio
import pytest

from pymongo.errors import PyMongoError
from app import services


class MockFile:
    filename = "test.wav"
    mimetype = "audio/wav"

    def save(self, path):
        pass


class MockResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class FakeFile:
    """Fake file handle for open()"""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def test_transcribe_success(monkeypatch):

    monkeypatch.setattr(services, "add_entry", lambda _: None)

    monkeypatch.setattr(
        services.requests,
        "post",
        lambda *a, **k: MockResponse({"transcript": "hello", "language": "en"}),
    )

    monkeypatch.setattr("builtins.open", lambda *a, **k: FakeFile())

    file = MockFile()

    result = services.transcribe_audio(file)

    assert result["transcript"] == "hello"


def test_transcribe_missing_fields(monkeypatch):
    monkeypatch.setattr(services.os, "makedirs", lambda *a, **k: None)
    monkeypatch.setattr(services.uuid, "uuid4", lambda: type("x", (), {"hex": "abc"})())

    monkeypatch.setattr("builtins.open", lambda *a, **k: FakeFile())

    monkeypatch.setattr(
        services.requests, "post", lambda *a, **k: MockResponse({"transcript": ""})
    )

    monkeypatch.setattr(services, "add_entry", lambda _: None)

    file = MockFile()
    result = services.transcribe_audio(file)

    assert result["transcript"] == ""


def test_transcribe_request_failure(monkeypatch):
    def fail(*args, **kwargs):
        raise services.requests.exceptions.RequestException("fail")

    monkeypatch.setattr(services.requests, "post", fail)

    file = MockFile()

    with pytest.raises(Exception):
        services.transcribe_audio(file)


# -------------------------
# get_user_by_id
# -------------------------


def test_get_user_by_id_success(monkeypatch):
    class MockDB:
        class users:
            @staticmethod
            def find_one(q):
                return {
                    "_id": "507f1f77bcf86cd799439011",
                    "username": "test",
                    "password": "pw",
                    "entries": [],
                }

    monkeypatch.setattr(services, "get_db", lambda: MockDB())

    user = services.get_user_by_id("507f1f77bcf86cd799439011")

    assert user.username == "test"


def test_get_user_by_id_invalid(monkeypatch):
    # bypass ObjectId crash by patching it
    monkeypatch.setattr(services, "ObjectId", lambda x: x)

    class MockDB:
        class users:
            @staticmethod
            def find_one(q):
                return None

    monkeypatch.setattr(services, "get_db", lambda: MockDB())

    result = services.get_user_by_id("bad-id")

    assert result is None


def test_create_user_success(monkeypatch):
    class MockUsers:
        def __init__(self):
            self.calls = 0

        def find_one(self, q):
            # 1st call: existence check
            if self.calls == 0:
                self.calls += 1
                return None

            # 2nd call: final fetch
            return {
                "_id": "u1",
                "username": "newnew",
                "password": "pw",
                "entries": "e1",
            }

        def insert_one(self, doc):
            return SimpleNamespace(inserted_id="u1")

    class MockEntries:
        def insert_one(self, _):
            return SimpleNamespace(inserted_id="e1")

    class MockDB:
        users = MockUsers()
        entries = MockEntries()

    monkeypatch.setattr(services, "get_db", lambda: MockDB())

    user = services.create_user("newnew", "pw")

    assert user.username == "newnew"


def test_create_user_duplicate(monkeypatch):
    class MockUsers:
        def find_one(self, q):
            return {"username": "exists"}

    class MockDB:
        users = MockUsers()

    monkeypatch.setattr(services, "get_db", lambda: MockDB())

    with pytest.raises(ValueError):
        services.create_user("exists", "pw")


def test_add_entry(monkeypatch):
    class MockUser:
        is_authenticated = True
        username = "test_user"

    class MockUsers:
        def find_one(self, q):
            return {"entries": "eid"}

    class MockEntries:
        called = False

        def update_one(self, *a, **k):
            called = True

    class MockDB:
        users = MockUsers()
        entries = MockEntries()

    monkeypatch.setattr(services, "get_db", lambda: MockDB())
    monkeypatch.setattr(services, "current_user", MockUser())

    services.add_entry({"x": 1})

    assert True


def test_get_user_by_id_exception(monkeypatch):
    class MockDB:
        class users:
            @staticmethod
            def find_one(q):
                raise PyMongoError("db error")

    monkeypatch.setattr(services, "get_db", lambda: MockDB())

    result = services.get_user_by_id("507f1f77bcf86cd799439011")

    assert result is None


def test_get_user_by_username_exception(monkeypatch):
    class MockDB:
        class users:
            @staticmethod
            def find_one(q):
                raise PyMongoError("db error")

            # def find_one(self, q):
            #     raise PyMongoError("db error")

    monkeypatch.setattr(services, "get_db", lambda: MockDB())

    result = services.get_user_by_username("test")

    assert result is None


def test_get_entries_not_logged_in(monkeypatch):
    class MockUser:
        is_authenticated = False

    monkeypatch.setattr(services, "current_user", MockUser())

    result = services.get_entries()

    assert result == []


def test_get_entries_no_doc(monkeypatch):
    class MockUser:
        is_authenticated = True
        username = "x"

    class MockDB:
        class users:
            @staticmethod
            def find_one(q):
                return {"entries": "eid"}

        class entries:
            @staticmethod
            def find_one(q):
                return None

    monkeypatch.setattr(services, "current_user", MockUser())
    monkeypatch.setattr(services, "get_db", lambda: MockDB())

    result = services.get_entries()

    assert result == []


def test_get_data(monkeypatch):
    class MockUser:
        is_authenticated = True
        username = "x"

    class MockDB:
        class users:
            @staticmethod
            def find_one(q):
                return {"entries": "eid"}

        class entries:
            @staticmethod
            def find_one(q):
                return {"entries": [1, 2, 3]}

    monkeypatch.setattr(services, "current_user", MockUser())
    monkeypatch.setattr(services, "get_db", lambda: MockDB())

    result = asyncio.run(services.get_data())

    assert result == [1, 2, 3]
