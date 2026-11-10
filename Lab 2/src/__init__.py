"""Monoalphabetic cryptanalysis package for English ciphertexts."""

from .corpus import (
    ENGLISH_UNIGRAM_FREQS,
    ENGLISH_ALPHABET,
    ENGLISH_IC,
    RANDOM_IC,
    TOP_BIGRAMS,
    TOP_TRIGRAMS,
)
from .analyzer import (
    calculate_unigram_frequencies,
    calculate_relative_frequencies,
    calculate_index_of_coincidence,
    calculate_chi_squared,
    extract_ngrams,
    extract_doubles,
    extract_single_letter_words,
)
from .variants import (
    get_variant,
    resolve_variant_number,
    list_available_variants,
)
from .solver import (
    SubstitutionState,
    ORIGINAL_DECODE,
)

__all__ = [
    "ENGLISH_UNIGRAM_FREQS",
    "ENGLISH_ALPHABET",
    "ENGLISH_IC",
    "RANDOM_IC",
    "TOP_BIGRAMS",
    "TOP_TRIGRAMS",
    "calculate_unigram_frequencies",
    "calculate_relative_frequencies",
    "calculate_index_of_coincidence",
    "calculate_chi_squared",
    "extract_ngrams",
    "extract_doubles",
    "extract_single_letter_words",
    "get_variant",
    "resolve_variant_number",
    "list_available_variants",
    "SubstitutionState",
    "ORIGINAL_DECODE",
]
