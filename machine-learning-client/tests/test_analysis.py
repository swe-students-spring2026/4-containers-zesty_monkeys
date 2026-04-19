"""
Test for analysis.py
"""

import sys
from unittest.mock import MagicMock, patch
import pytest
from app import analysis

mock_db = MagicMock()
mock_db.FILLER_WORDS = ["uh", "um", "like", "basically", "you know"]
mock_db.SENTENCE_LENGTH_THRESHOLD = [10, 20]  # Short < 10, Average < 20, Long >= 20
mock_db.CLAUSE_LENGTH_THRESHOLD = [5, 10]  # Short < 5, Average < 10, Long >= 10
mock_db.STOP_WORDS = {"the", "a", "an", "is", "it", "in", "on", "at", "to", "and", "of"}
sys.modules["analysis_db"] = mock_db


@pytest.fixture(autouse=True)
def mock_analysis_db():
    """
    Overwrite the original analysis_db with a mock_db.
    """
    with patch("app.analysis.analysis_db", mock_db):
        yield


class TestCountFillerWords:
    """
    Test class for function count_filler_words.
    """

    def test_no_filler_words(self):
        """
        Test a sentence with zero filler words.
        """
        assert analysis.count_filler_words("This is a clean sentence.") == 0

    def test_filler_words_count(self):
        """
        Test the number of filler words in a sentence.
        """
        assert analysis.count_filler_words("I was like, um, I uh don't know.") == 3

    def test_duplicate_filler_words(self):
        """
        Test a sentence with duplicated filler words.
        """
        assert analysis.count_filler_words("uh uh uh") == 3

    def test_case_insensitive(self):
        """
        Test if the function is case insensitive.
        """
        assert analysis.count_filler_words("Uh uM BASICALLY") == 3

    def test_multi_word_filler(self):
        """
        Test a sentence with a multi-word filler phrase (you know).
        """
        assert analysis.count_filler_words("This is, you know, mind blowing.") == 1

    def test_only_partial_match(self):
        """
        Test if a word that contains a filler word (like in likewise) will be misidentified.
        """
        assert analysis.count_filler_words("Likewise.") == 0


class TestSentenceLengthRating:
    """
    Test class for function sentence_length_rating.
    """

    def _make_sentence(self, word_count: int) -> str:
        """
        Return a single sentence (one period) with exactly word_count words.
        """
        return " ".join(["word"] * word_count) + "."

    def test_short_sentence(self):
        """
        Test a 5-word (short) sentence.
        """
        assert analysis.sentence_length_rating(self._make_sentence(5)) == "Short"

    def test_average_sentence(self):
        """
        Test a 15-word (average) sentence.
        """
        assert analysis.sentence_length_rating(self._make_sentence(15)) == "Average"

    def test_long_sentence(self):
        """
        Test a 25-word (short) sentence.
        """
        assert analysis.sentence_length_rating(self._make_sentence(25)) == "Long"

    def test_multiple_sentences(self):
        """
        Test two sentences with an average length of 5 words.
        """
        speech = "One two three four five. Six seven eight nine ten."
        assert analysis.sentence_length_rating(speech) == "Short"

    def test_question_mark_splits_sentences(self):
        """
        Test punctuation detection between sentences.
        """
        speech = "Is this; short?! Yes, it is!!!"
        assert analysis.sentence_length_rating(speech) == "Short"

    def test_boundary_short_to_average(self):
        """
        Test the boundary from short to average.
        """
        assert analysis.sentence_length_rating(self._make_sentence(10)) == "Average"

    def test_boundary_average_to_long(self):
        """
        Test the boundary from average to long.
        """
        assert analysis.sentence_length_rating(self._make_sentence(20)) == "Long"


class TestClauseLengthRating:
    """
    Test class for function clause_length_rating.
    """

    def test_short_clauses(self):
        """
        Test for 3 clauses with an average length of 2 words
        """
        speech = "one two, three four, five six"
        assert analysis.clause_length_rating(speech) == "Short"

    def test_average_clauses(self):
        """
        Test for 2 clauses with an average length of 6 words
        """
        speech = "one two three four five six, seven eight nine ten eleven twelve"
        assert analysis.clause_length_rating(speech) == "Average"

    def test_long_clauses(self):
        """
        Test for a single long clause
        """
        speech = " ".join(["word"] * 20)
        assert analysis.clause_length_rating(speech) == "Long"

    def test_semicolon_splits_clause(self):
        """
        Test for semicolons
        """
        speech = "a b c; d e f"
        assert analysis.clause_length_rating(speech) == "Short"

    def test_boundary_short_to_average(self):
        """
        Test for boundry between short and average
        """
        speech = "one two three four five, six seven eight nine ten"
        assert analysis.clause_length_rating(speech) == "Average"


BASE_SPEECH = (
    "The climate crisis is the defining challenge of our time. "
    "We must address the climate crisis with urgency and determination. "
    "The climate crisis affects every nation, every community, every family. "
    "Our response to the climate crisis will define our legacy. "
    "Together we can overcome the climate crisis through innovation and cooperation. "
    "The climate crisis demands bold action, bold leadership, and bold commitment."
)


class TestWordFrequency:
    """
    Test class for function word_frequency.
    """

    def test_overused_words_detected(self):
        """
        Test that words appearing at or above the threshold are returned.
        climate and crisis each appear 6 times in BASE_SPEECH.
        """
        result = analysis.word_frequency(BASE_SPEECH, phrase_lengths=[])
        words = [word for word, _ in result["overused_words"]]
        assert "climate" in words
        assert "crisis" in words

    def test_overused_words_correct_counts(self):
        """
        Test that the reported counts for overused words are accurate.
        """
        result = analysis.word_frequency(BASE_SPEECH, phrase_lengths=[])
        word_counts = dict(result["overused_words"])
        assert word_counts["climate"] == 6
        assert word_counts["crisis"] == 6

    def test_overused_words_descending_order(self):
        """
        Test that overused words are returned in descending order of frequency.
        """
        result = analysis.word_frequency(BASE_SPEECH, phrase_lengths=[])
        counts = [count for _, count in result["overused_words"]]
        assert counts == sorted(counts, reverse=True)

    def test_stop_words_excluded_from_overused_words(self):
        """
        Test that stop words are not included in overused_words.
        """
        result = analysis.word_frequency(BASE_SPEECH, phrase_lengths=[])
        words = [word for word, _ in result["overused_words"]]
        for stop_word in mock_db.STOP_WORDS:
            assert stop_word not in words

    def test_short_words_excluded_by_min_word_length(self):
        """
        Test that words shorter than min_word_length are excluded,
        for example, "we" is less than 3 letters.
        """
        result = analysis.word_frequency(
            BASE_SPEECH, min_word_length=3, phrase_lengths=[]
        )
        words = [word for word, _ in result["overused_words"]]
        assert "we" not in words

    def test_threshold_filters_infrequent_words(self):
        """
        Test that words appearing fewer times than the threshold are excluded.
        """
        result = analysis.word_frequency(BASE_SPEECH, threshold=3, phrase_lengths=[])
        words = [word for word, _ in result["overused_words"]]
        assert "urgency" not in words

    def test_top_n_limits_results(self):
        """
        Test that no more than top_n words are returned.
        """
        result = analysis.word_frequency(BASE_SPEECH, top_n=2, phrase_lengths=[])
        assert len(result["overused_words"]) <= 2

    def test_phrase_detection(self):
        """
        Test that a repeated phrase is detected.
        'the climate crisis' appears 6 times in BASE_SPEECH.
        """
        result = analysis.word_frequency(BASE_SPEECH, phrase_lengths=[3])
        assert 3 in result["overused_phrases"]
        phrases = [phrase for phrase, _ in result["overused_phrases"][3]]
        assert "the climate crisis" in phrases

    def test_phrase_correct_count(self):
        """
        Test that the count reported for a detected phrase is accurate.
        """
        result = analysis.word_frequency(BASE_SPEECH, phrase_lengths=[3])
        phrase_counts = dict(result["overused_phrases"][3])
        assert phrase_counts["the climate crisis"] == 6

    def test_phrase_lengths_key_absent_when_no_qualifying_phrases(self):
        """
        Test that a phrase-length key is absent from overused_phrases
        when no phrases meet the threshold.
        Testing with a very high threshold so that no 2-grams should qualify.
        """
        result = analysis.word_frequency(BASE_SPEECH, phrase_lengths=[2], threshold=100)
        assert 2 not in result["overused_phrases"]

    def test_empty_phrase_lengths_returns_no_phrases(self):
        """
        Test that passing an empty phrase_lengths list returns an empty overused_phrases dict.
        """
        result = analysis.word_frequency(BASE_SPEECH, phrase_lengths=[])
        assert not result["overused_phrases"]

    def test_returns_expected_keys(self):
        """
        Test that the result always contains 'overused_words' and 'overused_phrases' keys.
        """
        result = analysis.word_frequency(BASE_SPEECH, phrase_lengths=[])
        assert "overused_words" in result
        assert "overused_phrases" in result

    def test_no_overused_words_below_threshold(self):
        """
        Test that an empty list is returned when no words meet the threshold.
        """
        result = analysis.word_frequency("hello world", threshold=5, phrase_lengths=[])
        assert result["overused_words"] == []


BASE_ERROR_SPEECH = (
    "Good morning everyones!"
    "I is very happy to be here today and speaked to all of you wonderful peoples."
    "You know, life are full of challenges. "
    "Many of us, we has faced difficult times — "
    "times where we doesn't know what to do or where to go."
    "But I wants to tell you something important: never give up on you're dreams!"
    "When I was a young boy, my mother always telled me, 'Son, work hardly and you will succeed.'"
    "And I thinked about them words every single day."
    "She were the most wisest person I ever knowed."
)


class TestCorrectGrammarErrors:
    """
    Test class for function correct_grammar_errors.
    The tests in this class are mainly things like return types,
    due to the complexity and uncertainty of the NLP model's actual output.
    """

    def test_returns_list(self):
        """
        correct_grammar_errors should always return a list.
        """
        result = analysis.correct_grammar_errors(BASE_ERROR_SPEECH)
        assert isinstance(result, list)

    def test_returns_list_of_grammar_error_instances(self):
        """
        Every item in the returned list should be a GrammarErrorInstance.
        """
        result = analysis.correct_grammar_errors(BASE_ERROR_SPEECH)
        assert len(result) > 0, "Expected at least one error to be detected"
        for item in result:
            assert isinstance(item, analysis.GrammarErrorInstance)

    def test_grammar_error_instance_fields_are_correct_types(self):
        """
        Each GrammarErrorInstance should have fields of the expected types.
        """
        result = analysis.correct_grammar_errors(BASE_ERROR_SPEECH)
        assert len(result) > 0, "Expected at least one error to be detected"
        for item in result:
            assert isinstance(item.error_offset, int)
            assert isinstance(item.error_length, int)
            assert isinstance(item.message, str)
            assert isinstance(item.replacements, list)

    def test_empty_string_returns_empty_list(self):
        """
        An empty input string should return an empty list with no errors.
        """
        result = analysis.correct_grammar_errors("")
        assert not result

    def test_correct_speech_returns_empty_list(self):
        """
        A grammatically correct sentence should return no errors.
        """
        correct_speech = "Good morning, everyone! I am very happy to be here today."
        result = analysis.correct_grammar_errors(correct_speech)
        assert not result

    def test_error_offsets_are_within_bounds(self):
        """
        Every error offset should be a valid index within the input string.
        """
        result = analysis.correct_grammar_errors(BASE_ERROR_SPEECH)
        for item in result:
            assert 0 <= item.error_offset < len(BASE_ERROR_SPEECH)

    def test_error_offsets_are_non_negative(self):
        """
        Error offsets and lengths should never be negative.
        """
        result = analysis.correct_grammar_errors(BASE_ERROR_SPEECH)
        for item in result:
            assert item.error_offset >= 0
            assert item.error_length >= 0
