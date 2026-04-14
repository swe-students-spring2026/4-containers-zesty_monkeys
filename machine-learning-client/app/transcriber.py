"""
Whisper audio transcription. Handles loading the model, validating audio files, transcribing audio,
and computing words-per-minute. Maybe more to be added.
"""

import os
import logging

import whisper

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a"}


def load_model(model_size: str = "base") -> whisper.Whisper:
    """
    Load a Whisper model of size of "tiny", "base", "small", "medium", or "large".
    Returns a loaded Whisper model instance.
    Raises ValueError if model_size is not a recognised Whisper model name.
    """
    valid_sizes = {"tiny", "base", "small", "medium", "large"}
    if model_size not in valid_sizes:
        raise ValueError(
            f"Invalid model size '{model_size}'. Must be one of: {valid_sizes}"
        )

    logger.info("Loading Whisper model: %s", model_size)
    return whisper.load_model(model_size)


def validate_audio_file(audio_path: str) -> bool:
    """
    Check that a file exists and is an audio file.
    Returns True if the file exists and has valid extension.
    Raises FileNotFoundError if the file does not exist and ValueError if the file extension is
    invalid.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    _, ext = os.path.splitext(audio_path)
    if ext.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported audio format '{ext}'. "
            f"Supported formats: {SUPPORTED_EXTENSIONS}"
        )

    return True


def transcribe_audio(
        model: whisper.Whisper,
        audio_path: str,
        initial_prompt: str = "Um, uh, like, you know, so, actually, basically, right,",
    ) -> dict:
    """
    Transcribe a (validated) audio file using a loaded Whisper model.
    Returns a dictionary with "text" (full transcript), "segments" (timed segment dictionary with
    "start", "end", and "text"), and "language" (the detected language).
    Raises FileNotFoundError if the file does not exist and ValueError if the file extension is
    invalid.
    """
    validate_audio_file(audio_path)

    logger.info("Transcribing: %s", audio_path)
    result = model.transcribe(
        audio_path,
        no_speech_threshold=0.6,
        condition_on_previous_text=True,
        initial_prompt=initial_prompt,
    )

    return {
        "text": result.get("text", "").strip(),
        "segments": result.get("segments", []),
        "language": result.get("language", "unknown"),
    }


def extract_words_per_minute(segments: list) -> float:
    """
    Compute words per minute from segments.
    Returns WPM as a float, 0.0 if segments is empty or audio duration is zero.
    """
    if not segments:
        return 0.0

    total_words = sum(len(seg.get("text", "").split()) for seg in segments)

    duration_seconds = segments[-1].get("end", 0.0) - segments[0].get("start", 0.0)
    if duration_seconds <= 0:
        return 0.0

    duration_minutes = duration_seconds / 60.0
    return round(total_words / duration_minutes, 2)

# perhaps another function that gives qualitative value to pauses / splitting of a sentence with segments