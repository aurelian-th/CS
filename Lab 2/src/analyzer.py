"""Statistical cryptanalysis and linguistic metrics for ciphertext evaluation."""

import re
from collections import Counter
from typing import Dict, List, Tuple
from .corpus import (
    ENGLISH_ALPHABET,
    ENGLISH_UNIGRAM_FREQS,
    ENGLISH_IC,
    RANDOM_IC,
)


def filter_letters_only(text: str) -> str:
    """Extract uppercase alphabetical characters from text."""
    return "".join(c.upper() for c in text if c.isalpha())


def calculate_unigram_frequencies(text: str) -> Dict[str, int]:
    """Calculate raw occurrence counts for all 26 Latin letters."""
    counts = {c: 0 for c in ENGLISH_ALPHABET}
    for char in text:
        if char.isalpha():
            counts[char.upper()] += 1
    return counts


def calculate_relative_frequencies(text: str) -> Dict[str, float]:
    """Calculate percentage frequencies for all 26 Latin letters."""
    raw = calculate_unigram_frequencies(text)
    total = sum(raw.values())
    if total == 0:
        return {c: 0.0 for c in ENGLISH_ALPHABET}
    return {c: (cnt / total) * 100.0 for c, cnt in raw.items()}


def calculate_index_of_coincidence(text: str) -> float:
    """
    Calculate the Index of Coincidence (IC) of the text.

    Formula:
        IC = sum(f_i * (f_i - 1)) / (N * (N - 1))

    Where f_i is the count of letter i and N is the total letter count.
    Standard English text yields IC ≈ 0.0667, while uniform random text yields ≈ 0.0385.
    """
    raw = calculate_unigram_frequencies(text)
    total = sum(raw.values())
    if total <= 1:
        return 0.0
    numerator = sum(cnt * (cnt - 1) for cnt in raw.values())
    denominator = total * (total - 1)
    return numerator / denominator


def calculate_chi_squared(text: str, reference_freqs: Dict[str, float] = None) -> float:
    """
    Compute the Chi-squared goodness-of-fit statistic against reference frequencies.

    Formula:
        chi^2 = sum((O_i - E_i)^2 / E_i)
    """
    if reference_freqs is None:
        reference_freqs = ENGLISH_UNIGRAM_FREQS

    raw = calculate_unigram_frequencies(text)
    total = sum(raw.values())
    if total == 0:
        return 0.0

    chi_sq = 0.0
    for char in ENGLISH_ALPHABET:
        observed = raw[char]
        expected = (reference_freqs[char] / 100.0) * total
        if expected > 0:
            chi_sq += ((observed - expected) ** 2) / expected
    return chi_sq


def extract_ngrams(text: str, n: int = 2) -> List[Tuple[str, int]]:
    """
    Extract n-grams (bigrams n=2, trigrams n=3, etc.) within word boundaries.
    Returns list of (ngram, count) tuples sorted descending by frequency.
    """
    words = [re.sub(r"[^A-Za-z]", "", w).upper() for w in text.split()]
    counter: Counter[str] = Counter()
    for word in words:
        if len(word) >= n:
            for i in range(len(word) - n + 1):
                counter[word[i : i + n]] += 1
    return counter.most_common()


def extract_doubles(text: str) -> List[Tuple[str, int]]:
    """Extract doubled adjacent letters (e.g., 'OO', 'SS')."""
    words = [re.sub(r"[^A-Za-z]", "", w).upper() for w in text.split()]
    counter: Counter[str] = Counter()
    for word in words:
        for i in range(len(word) - 1):
            if word[i] == word[i + 1]:
                counter[word[i : i + 2]] += 1
    return counter.most_common()


def extract_single_letter_words(text: str) -> List[Tuple[str, int]]:
    """Extract isolated single-letter words delimited by whitespace or punctuation."""
    tokens = re.findall(r"(?:\b|\s)([A-Za-z])(?:\b|\s)", text)
    counter = Counter(t.upper() for t in tokens)
    return counter.most_common()


def get_sorted_unigrams(text: str) -> List[Tuple[str, int, float]]:
    """
    Return unigram analysis sorted by descending frequency.
    Each element: (character, count, percentage).
    """
    raw = calculate_unigram_frequencies(text)
    total = sum(raw.values())
    sorted_chars = sorted(raw.keys(), key=lambda c: raw[c], reverse=True)
    results = []
    for c in sorted_chars:
        cnt = raw[c]
        pct = (cnt / total * 100.0) if total > 0 else 0.0
        results.append((c, cnt, pct))
    return results
