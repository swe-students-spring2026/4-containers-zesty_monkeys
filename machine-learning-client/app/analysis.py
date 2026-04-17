"""
A library for transcript analysis. 
"""

import re
from collections import Counter
import analysis_db

def count_filler_words (speech : str):
    """
    Count the number of filler words (like, uh, etc.) in a speech transcript.
    The list of filler words is in analysis_db.py.
    """
    count = 0
    for filler_word in analysis_db.FILLER_WORDS:
        count += speech.lower().count(filler_word)
    return count

def speech_speed_rating (speech : str, time_sec : int):
    """
    Rate the speed of a speech.
    Outputs a string, and can be "Too slow", "Slow", "Average", "Fast" or "Too fast".
    """
    word_count = len(speech.split(" ")) - count_filler_words(speech) # Excludes filler words
    speed = word_count / time_sec * 60
    rating = ""
    match speed:
        case num if num < analysis_db.WORDS_PER_MINUTE_THRESHOLD[0]:
            rating = "Too slow"
        case num if num < analysis_db.WORDS_PER_MINUTE_THRESHOLD[1]:
            rating = "Slow"
        case num if num < analysis_db.WORDS_PER_MINUTE_THRESHOLD[2]:
            rating = "Average"
        case num if num < analysis_db.WORDS_PER_MINUTE_THRESHOLD[3]:
            rating = "Fast"
        case _:
            rating = "Too fast"
    return rating

def sentence_length_rating (speech : str):
    """
    Rate the length (the number of words) in a sentence. 
    Sentences are divided by periods, question marks or exclamation marks.
    Outputs a string, and can be "Short", "Average" or "Long".
    """
    word_count = len(speech.split(" "))
    sentence_count = len(re.split(r"[.?!]", speech))
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

def clause_length_rating (speech : str):
    """
    Rate the length (the number of words) in a clause.
    A clause is a part of a sentence. Clauses are divided by commas and semicolons.
    Outputs a string, and can be "Short", "Average" or "Long".
    """
    word_count = len(speech.split(" "))
    clause_count = len(re.split(r"[,.;?!]", speech))
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


def word_frequency (speech : str, top_n : int = 10,
                    min_word_length : int = 3,
                    phrase_lengths : list[int] | None = None,
                    threshold : int = 3):
    """
    Finds the top n words, and the top n phrases that appears (hence overused) in a speech.
    Words exclude stop words and filler words. Phrases only exlude stop words.
    Returns an object with two attibutes: "overused_words" and "overused_phrases",
    which are both lists that contain the top n appearing words/phrases, descending order.
    """
    tokens = re.sub(r"[^\w\s]", "", speech.lower()).split()
    filtered_tokens = [
        t for t in tokens
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
        ngrams = [
            " ".join(tokens[i : i + n])
            for i in range(len(tokens) - n + 1)
        ]

        # This only keeps phrases that are not entirely stop words
        meaningful_n_grams = [
            phrase for phrase in ngrams
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
