"""English linguistic statistics and reference corpora.

Includes frequency tables, n-grams, and theoretical benchmarks
derived from the laboratory assignment specification (Table 2.2).
"""

from typing import Dict, List, Tuple

ENGLISH_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Table 2.2 from laboratory specification: Letter frequencies in English (%)
ENGLISH_UNIGRAM_FREQS: Dict[str, float] = {
    "A": 8.17,
    "B": 1.49,
    "C": 2.78,
    "D": 4.25,
    "E": 12.70,
    "F": 2.23,
    "G": 2.01,
    "H": 6.09,
    "I": 6.97,
    "J": 0.15,
    "K": 0.77,
    "L": 4.03,
    "M": 2.41,
    "N": 6.75,
    "O": 7.51,
    "P": 1.93,
    "Q": 0.09,
    "R": 5.99,
    "S": 6.33,
    "T": 9.06,
    "U": 2.76,
    "V": 0.98,
    "W": 2.36,
    "X": 0.15,
    "Y": 1.97,
    "Z": 0.07,
}

# English letters sorted by descending frequency
ENGLISH_LETTERS_BY_FREQ: List[str] = sorted(
    ENGLISH_UNIGRAM_FREQS.keys(),
    key=lambda c: ENGLISH_UNIGRAM_FREQS[c],
    reverse=True,
)

# Prominent English bigrams as documented in laboratory assignment
TOP_BIGRAMS: List[str] = [
    "TH", "HE", "IN", "ER", "AN", "RE", "ED", "ON",
    "ES", "ST", "EN", "AT", "TO", "NT", "HA", "ND",
    "OU", "EA", "NG", "AS", "OR", "TI", "IS", "ET",
    "IT", "AR", "TE", "SE", "HI", "OF",
]

# Prominent English trigrams as documented in laboratory assignment
TOP_TRIGRAMS: List[str] = [
    "THE", "AND", "THA", "ENT", "ION", "TIO", "FOR",
    "NDE", "HAS", "NCE", "TIS", "OFT", "MEN",
]

# Prominent doubled letters in English
COMMON_DOUBLES: List[str] = ["SS", "EE", "TT", "FF", "LL", "MM", "OO"]

# Single-letter words in English
SINGLE_LETTER_WORDS: List[str] = ["A", "I"]

# Theoretical Index of Coincidence (IC)
ENGLISH_IC: float = 0.0667
RANDOM_IC: float = 1.0 / 26.0  # ~0.03846

