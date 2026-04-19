"""
A library for transcript analysis.
"""

import re
from dataclasses import dataclass, field
from collections import Counter
import language_tool_python
from . import analysis_db


@dataclass
class GrammarErrorInstance:
    """
    A class that represents a possible grammar error.
    error_offset is the error's first letter's index in the original text.
    error_length is the length of the error.
    message is the explanation and suggestion for the error.
    replacement is a list of possible fixes for the error.
    """

    error_offset: int = 0
    error_length: int = 0
    message: str = ""
    replacements: list[str] = field(default_factory=list)


def count_filler_words(speech: str):
    """
    Count the number of filler words (like, uh, etc.) in a speech transcript.
    The list of filler words is in analysis_db.py.
    """
    count = 0
    for filler_word in analysis_db.FILLER_WORDS:
        pattern = rf"\b{re.escape(filler_word)}\b"
        count += len(re.findall(pattern, speech.lower()))
    return count


def sentence_length_rating(speech: str):
    """
    Rate the length (the number of words) in a sentence.
    Sentences are divided by periods, question marks or exclamation marks.
    Outputs a string, and can be "Short", "Average" or "Long".
    """
    word_count = len(speech.split(" "))
    sentence_count = len([s for s in re.split(r"[.?!]", speech) if s.strip()])
    speed = word_count / sentence_count
    rating = ""
    match speed:
        case num if num < analysis_db.SENTENCE_LENGTH_THRESHOLD[0]:
            rating = "Short"
        case num if num < analysis_db.SENTENCE_LENGTH_THRESHOLD[1]:
            rating = "Average"
        case _:
            rating = "Long"
    return rating


def clause_length_rating(speech: str):
    """
    Rate the length (the number of words) in a clause.
    A clause is a part of a sentence. Clauses are divided by commas and semicolons.
    Outputs a string, and can be "Short", "Average" or "Long".
    """
    word_count = len(speech.split(" "))
    clause_count = len([s for s in re.split(r"[.?!,;:\"]", speech) if s.strip()])
    speed = word_count / clause_count
    rating = ""
    match speed:
        case num if num < analysis_db.CLAUSE_LENGTH_THRESHOLD[0]:
            rating = "Short"
        case num if num < analysis_db.CLAUSE_LENGTH_THRESHOLD[1]:
            rating = "Average"
        case _:
            rating = "Long"
    return rating


def word_frequency(
    speech: str,
    top_n: int = 10,
    min_word_length: int = 3,
    phrase_lengths: list[int] | None = None,
    threshold: int = 3,
):
    """
    Finds the top n words, and the top n phrases that appears (hence overused) in a speech.
    Words exclude stop words and filler words. Phrases only exlude stop words.
    Returns an object with two attibutes: "overused_words" and "overused_phrases",
    which are both lists that contain the top n appearing words/phrases, descending order.
    """
    tokens = re.sub(r"[^\w\s]", "", speech.lower()).split()
    filtered_tokens = [
        t
        for t in tokens
        if t not in analysis_db.STOP_WORDS and len(t) >= min_word_length
    ]
    word_counts = Counter(filtered_tokens)
    overused_words = [
        (word, count)
        for word, count in word_counts.most_common(top_n)
        if count >= threshold
    ]

    # Stop words will be included in phrases
    overused_phrases: dict[int, list[tuple[str, int]]] = {}
    for n in phrase_lengths:
        ngrams = [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]

        # This only keeps phrases that are not entirely stop words
        meaningful_n_grams = [
            phrase
            for phrase in ngrams
            if any(
                w not in analysis_db.STOP_WORDS and len(w) >= min_word_length
                for w in phrase.split()
            )
        ]
        phrase_counts = Counter(meaningful_n_grams)
        top_phrases = [
            (phrase, count)
            for phrase, count in phrase_counts.most_common(top_n)
            if count >= threshold
        ]

        if top_phrases:
            overused_phrases[n] = top_phrases

    return {
        "overused_words": overused_words,
        "overused_phrases": overused_phrases,
    }


def correct_grammar_errors(speech: str):
    """
    Finds the possible grammar mistakes in a transcript.
    Returns a list of GrammarErrorInstance objects,
    which includes the error's offset, length, message and replacements
    """
    tool = language_tool_python.LanguageTool("en-US")
    matches = tool.check(speech)
    grammar_errors = []
    for m in matches:
        if m.category.lower() not in analysis_db.ERROR_CATEGORIES:
            continue
        grammar_error = GrammarErrorInstance()
        grammar_error.error_offset = m.offset
        grammar_error.error_length = m.error_length
        grammar_error.message = m.message
        grammar_error.replacements = m.replacements
        grammar_errors.append(grammar_error)
    return grammar_errors
