"""
Tests for transcriber.py.
"""
from unittest.mock import MagicMock, patch
import pytest
from app import transcriber
from app.transcriber import (
    load_model,
    validate_audio_file,
    transcribe_audio,
    extract_words_per_minute,
)

# load_model

class TestLoadModel:
    @patch("app.transcriber.whisper.load_model")
    def test_valid_model_sizes_are_accepted(self, mock_load):
        mock_load.return_value = MagicMock()
        for size in ("tiny", "base", "small", "medium", "large"):
            result = load_model(size)
            mock_load.assert_called_with(size)
            assert result is mock_load.return_value

    def test_invalid_model_size_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid model size"):
            load_model("massive")

    def test_empty_model_size_raises_value_error(self):
        with pytest.raises(ValueError):
            load_model("")

    @patch("app.transcriber.whisper.load_model")
    def test_default_size_is_base(self, mock_load):
        mock_load.return_value = MagicMock()
        load_model()
        mock_load.assert_called_with("base")

# validate_audio_file

class TestValidateAudioFile:
    @pytest.mark.parametrize("ext", [".wav", ".mp3", ".m4a"])
    def test_valid_extensions_return_true(self, tmp_path, ext):
        audio = tmp_path / f"clip{ext}"
        audio.write_bytes(b"audio data placeholder")
        assert validate_audio_file(str(audio)) is True

    def test_missing_file_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            validate_audio_file("/not/a/real/path/audio.mp3")

    def test_unsupported_extension_raises_value_error(self, tmp_path):
        bad_file = tmp_path / "audio.bruh"
        bad_file.write_bytes(b"audio data placeholder")
        with pytest.raises(ValueError, match="Unsupported audio format"):
            validate_audio_file(str(bad_file))

    def test_extension_check_is_case_insensitive(self, tmp_path):
        audio = tmp_path / "audio.mp3"
        audio.write_bytes(b"audio data placeholder")
        assert validate_audio_file(str(audio)) is True

# transcribe_audio

class TestTranscribeAudio:
    def _make_model(self, transcribe_return: dict) -> MagicMock:
        model = MagicMock()
        model.transcribe.return_value = transcribe_return
        return model

    @patch("app.transcriber.validate_audio_file", return_value=True)
    def test_returns_expected_keys(self, _mock_validate):
        model = self._make_model({
            "text": "  Hello world  ",
            "segments": [{"start": 0, "end": 5, "text": "Hello world"}],
            "language": "en",
        })
        result = transcribe_audio(model, "fake.mp3")
        assert set(result.keys()) == {"text", "segments", "language"}

    @patch("app.transcriber.validate_audio_file", return_value=True)
    def test_text_is_stripped(self, _mock_validate):
        model = self._make_model({"text": "  Hello  ", "segments": [], "language": "en"})
        result = transcribe_audio(model, "fake.mp3")
        assert result["text"] == "Hello"

    @patch("app.transcriber.validate_audio_file", return_value=True)
    def test_segments_and_language_are_passed_through(self, _mock_validate):
        segments = [{"start": 0, "end": 3, "text": "Hi"}]
        model = self._make_model({"text": "Hi", "segments": segments, "language": "fr"})
        result = transcribe_audio(model, "fake.mp3")
        assert result["segments"] == segments
        assert result["language"] == "fr"

    @patch("app.transcriber.validate_audio_file", return_value=True)
    def test_missing_result_keys_default_gracefully(self, _mock_validate):
        model = self._make_model({})
        result = transcribe_audio(model, "fake.mp3")
        assert result["text"] == ""
        assert result["segments"] == []
        assert result["language"] == "unknown"

    @patch("app.transcriber.validate_audio_file", side_effect=FileNotFoundError("not found"))
    def test_propagates_file_not_found(self, _mock_validate):
        model = self._make_model({})
        with pytest.raises(FileNotFoundError):
            transcribe_audio(model, "missing.mp3")

    @patch("app.transcriber.validate_audio_file", side_effect=ValueError("bad ext"))
    def test_propagates_value_error_for_bad_extension(self, _mock_validate):
        model = self._make_model({})
        with pytest.raises(ValueError):
            transcribe_audio(model, "audio.bruh")

    @patch("app.transcriber.validate_audio_file", return_value=True)
    def test_default_initial_prompt_is_used(self, _mock_validate):
        model = self._make_model({"text": "", "segments": [], "language": "en"})
        transcribe_audio(model, "fake.mp3")
        _, kwargs = model.transcribe.call_args
        assert "initial_prompt" in kwargs
        assert "Um" in kwargs["initial_prompt"]

    @patch("app.transcriber.validate_audio_file", return_value=True)
    def test_custom_initial_prompt_is_forwarded(self, _mock_validate):
        model = self._make_model({"text": "", "segments": [], "language": "en"})
        transcribe_audio(model, "fake.mp3", initial_prompt="Custom prompt")
        _, kwargs = model.transcribe.call_args
        assert kwargs["initial_prompt"] == "Custom prompt"

# extract_words_per_minute

class TestExtractWordsPerMinute:
    def test_empty_segments_returns_zero(self):
        assert extract_words_per_minute([]) == 0.0

    def test_zero_duration_returns_zero(self):
        segments = [{"start": 5.0, "end": 5.0, "text": "hello world"}]
        assert extract_words_per_minute(segments) == 0.0

    def test_negative_duration_returns_zero(self):
        segments = [{"start": 10.0, "end": 5.0, "text": "hello"}]
        assert extract_words_per_minute(segments) == 0.0

    def test_correct_wpm_calculation(self):
        text = " ".join(["word"] * 60)
        segments = [{"start": 0.0, "end": 60.0, "text": text}]
        assert extract_words_per_minute(segments) == 60.0

    def test_wpm_is_rounded_to_two_decimal_places(self):
        segments = [{"start": 0.0, "end": 7.0, "text": " ".join(["word"] * 10)}]
        result = extract_words_per_minute(segments)
        assert result == round(result, 2)

    def test_multiple_segments_accumulate_word_counts(self):
        segments = [
            {"start": 0.0,  "end": 30.0, "text": "one two three"},
            {"start": 30.0, "end": 60.0, "text": "four five six"},
        ]
        assert extract_words_per_minute(segments) == 6.0

    def test_duration_uses_first_start_and_last_end(self):
        text = " ".join(["helloworld"] * 60)
        segments = [
            {"start": 10.0, "end": 40.0, "text": text[:20]},
            {"start": 40.0, "end": 70.0, "text": text[21:]},
        ]
        result = extract_words_per_minute(segments)
        total_words = sum(len(s["text"].split()) for s in segments)
        expected = round(total_words / 1.0, 2)  # 60s = 1 minute
        assert result == expected

    def test_segment_missing_text_key_counts_as_zero_words(self):
        segments = [{"start": 0.0, "end": 60.0}]
        assert extract_words_per_minute(segments) == 0.0

    def test_single_word_segment(self):
        segments = [{"start": 0.0, "end": 60.0, "text": "hello"}]
        assert extract_words_per_minute(segments) == 1.0
