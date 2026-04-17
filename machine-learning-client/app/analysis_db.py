"""
A mini database for speech analysis.
FILLER_WORDS: A list of filler words
WORDS_PER_MINUTE_THRESHOLD: Thresholds to determine the rating of a speech's speed.
SENTENCE_LENGTH_THRESHOLD: Thresholds to determine the rating of a sentence's length.
CLAUSE_LENGTH_THRESHOLD: Thresholds to determine the rating of a clause's length.
STOP_WORDS: A list of stop words to exclude when counting top N appearing words/phrases.
"""

FILLER_WORDS = ["uh", "oh", "like", "other", "you know"]

# Intervals: Too slow, slow, average, fast, too fast
WORDS_PER_MINUTE_THRESHOLD = [100, 120, 170, 240]

# Intervals: Short, average, long
SENTENCE_LENGTH_THRESHOLD = [10, 25]

# Intervals: Short, average, long
CLAUSE_LENGTH_THRESHOLD = [5, 10]
STOP_WORDS = [
  "a", "an", "the", "this", "that", "these", "those",

  "and", "but", "or", "for", "nor", "so", "yet", "at", "in", "on", "to", "from", "by", "of",

  "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",

  "is", "was", "were", "are", "am", "be", "been", "being", "do", "does", "did", "has", "have", "had"
]
