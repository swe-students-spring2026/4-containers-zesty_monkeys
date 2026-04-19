"""
Handles communication with the speech-to-text, text analysis, and LLM services.

Currently uses a stub implementation.
"""

import os
import requests
from bson import ObjectId
from flask_login import UserMixin, current_user
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# We will replace this with the actual ML service URL once it's implemented
ML_URL = os.environ.get("MLURL", "http://url-placeholder")


def transcribe_audio(file):
    """
    Sends raw audio file as a request to ML client,
    and retrieves the transcribed text.

    Args:
        file: Uploaded raw audio file
        (file: FileStorage object from Flask (request.files["audio"]))

    Returns:
        str: Transcribed text
    """
    url = f"{ML_URL}/transcribe"
    print(url)

    files = {"file": (file.filename, file.stream, file.mimetype)}
    # represents: (filename, (actual) file_object, content_type (like wav/mp3))

    try:
        response = requests.post(url, files=files, timeout=300)
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to connect to ML service: {e}"
        )

    data = response.json()
    add_entry(data)

    return data.get("transcript", "")
    # return {
    #     "transcript": data.get("transcript"),
    #     "segments": data.get("segments"),
    #     "language": data.get("language"),
    # }


# def analyze_text(transcript):
#     """
#     STUB code right now.
#     Simulates LLM-based speech analysis.

#     Args:
#         transcript (str): Raw transcription

#     Returns:
#         dict: Analysis results including cleaned text and feedback
#     """
#     return {
#         "cleaned_text": "This is a stub transcription.",
#         "feedback": "stub response."
#     }
# Returns:
#     dict: Analysis results including cleaned text and feedback
# """
# print(transcript)  # using this to fix linting errors for now, remove later
# return {
#     "cleaned_text": "This is a stub transcription.",
#     "feedback": "stub response.",
# }


def get_db():
    """
    Return the MongoDB instance and create connection.
    """
    if not hasattr(get_db, "db"):
        uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        dbname = os.environ.get("MONGO_DBNAME", "presentation_analyzer")
        # change db name later when natt gets back to me
        client = MongoClient(uri)
        get_db.db = client[dbname]
    return get_db.db


class User(UserMixin):
    """
    User model
    """

    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.username = user_doc["username"]
        self.password = user_doc["password"]
        self.entries = user_doc["entries"]


def get_user_by_id(user_id):
    """
    Look up user by their ObjectID string.
    """
    try:
        db = get_db()
        doc = db.users.find_one({"_id": ObjectId(user_id)})
        return User(doc) if doc else None
    except PyMongoError as exc:
        print("Error loading user %s: %s", user_id, exc)
        return None


def get_user_by_username(username):
    """
    Look up user by their username.
    """
    try:
        db = get_db()
        doc = db.users.find_one({"username": username})
        return User(doc) if doc else None
    except PyMongoError as exc:
        print("Error looking up username %s: %s", username, exc)
        return None


def create_user(username, password):
    """
    Create a user.
    """
    db = get_db()
    if db.users.find_one({"username": username}):
        raise ValueError(f"Username '{username}' is already taken.")

    entries = db.entries.insert_one({"entries": []})
    result = db.users.insert_one(
        {"username": username, "password": password, "entries": entries.inserted_id}
    )
    # add_entry()
    doc = db.users.find_one({"_id": result.inserted_id})
    return User(doc)


def add_entry(data):
    """
    Add user entry
    """
    db = get_db()
    if not current_user.is_authenticated:
        raise ValueError("Not logged in")
    entries = db.users.find_one({"username": current_user.username})["entries"]
    db.entries.update_one({"_id": entries}, {"$push": {"entries": data}})

async def get_data():
    """
    Get all past user data
    """
    db = get_db()
    if not current_user.is_authenticated:
        raise ValueError("Not logged in")
    entries = db.users.find_one({"username": current_user.username})["entries"]
    print(entries)
    return db.entries.find_one({"_id": entries})["entries"]