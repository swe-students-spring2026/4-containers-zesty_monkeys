"""
This file is for testing app/routes.py.
"""

# pylint: disable=too-few-public-methods, missing-docstring, unnecessary-lambda, unused-argument, invalid-name

import io

# import pytest
from flask import Response
from app import create_app, routes


class MockUser:
    is_authenticated = True
    username = "test"


class MockAnonymousUser:
    is_authenticated = False


def test_upload_audio_success(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    # mock login user
    monkeypatch.setattr(routes, "current_user", MockUser())

    # mock ML service
    def mock_transcribe(file):
        return {
            "transcript": "hello world",
            "language": "en",
            "analysis": {"score": 1},
            "audio_path": "abc.webm",
            "recorded_at": "now",
        }

    monkeypatch.setattr(routes, "transcribe_audio", mock_transcribe)

    data = {"audio": (io.BytesIO(b"fake"), "test.wav")}

    response = client.post("/upload", data=data)

    assert response.status_code == 200
    assert response.json["transcript"] == "hello world"
    assert response.json["language"] == "en"


def test_upload_audio_no_file(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockUser())

    response = client.post("/upload", data={})

    assert response.status_code == 500


def test_upload_audio_ml_failure(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockUser())

    def fail(file):
        raise routes.requests.exceptions.RequestException("fail")

    monkeypatch.setattr(routes, "transcribe_audio", fail)

    data = {"audio": (io.BytesIO(b"fake"), "test.wav")}

    response = client.post("/upload", data=data)

    assert response.status_code == 502
    assert "error" in response.json


def test_dashboard(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockUser())

    response = client.get("/")

    assert response.status_code == 200


def test_entries(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockUser())

    monkeypatch.setattr(routes, "get_entries", lambda: [{"a": 1}, {"b": 2}])

    response = client.get("/entries")

    assert response.status_code == 200
    assert response.json == [{"a": 1}, {"b": 2}]


def test_serve_audio(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockUser())

    def fake_send(directory, filename):

        return Response("ok", status=200)

    monkeypatch.setattr(routes, "send_from_directory", fake_send)

    response = client.get("/audio/test.webm")

    assert response.status_code == 200


def test_login_get(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockAnonymousUser())

    res = client.get("/login")
    assert res.status_code == 200


def test_login_redirect_if_authenticated(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockUser())

    res = client.get("/login")
    assert res.status_code in (301, 302)


def test_login_failure(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockAnonymousUser())
    monkeypatch.setattr(routes, "get_user_by_username", lambda u: None)

    res = client.post("/login", data={"username": "x", "password": "y"})

    assert res.status_code == 200


def test_register_get(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockAnonymousUser())

    res = client.get("/register")
    assert res.status_code == 200


def test_register_password_mismatch(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockAnonymousUser())

    res = client.post(
        "/register", data={"username": "a", "password": "1", "confirm_password": "2"}
    )

    assert res.status_code == 200


def test_register_success(monkeypatch):
    app = create_app()
    app.config["LOGIN_DISABLED"] = True
    client = app.test_client()

    monkeypatch.setattr(routes, "current_user", MockAnonymousUser())
    monkeypatch.setattr(routes, "create_user", lambda u, p: None)

    res = client.post(
        "/register", data={"username": "a", "password": "1", "confirm_password": "1"}
    )

    assert res.status_code in (301, 302)
