"""
Handles communication with the speech-to-text, text analysis, and LLM services.

Currently uses a stub implementation.
"""
import requests

# We will replace this with the actual ML service URL once it's implemented
ML_URL = "http://url-placeholder"

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
    url = ML_URL # or f"{ML_BASE_URL}/transcribe"

    files = {
        "file": (file.filename, file.stream, file.mimetype)
    }
    # represents: (filename, (actual) file_object, content_type (like wav/mp3))

    try:
        response = requests.post(url, files=files, timeout=10)
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException("Failed to connect to ML service:", e)

    data = response.json()

    return data.get("transcript", "")
    # return {
    #     "transcript": data.get("transcript"),
    #     "segments": data.get("segments"),
    #     "language": data.get("language"),
    # }

def analyze_text(transcript):
    """
    STUB code right now.
    Simulates LLM-based speech analysis.

    Args:
        transcript (str): Raw transcription

    Returns:
        dict: Analysis results including cleaned text and feedback
    """
    return {
        "cleaned_text": "This is a stub transcription.",
        "feedback": "stub response."
    }
