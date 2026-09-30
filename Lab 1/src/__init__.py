"""Romanian Caesar cipher package."""

from .alphabet import (
    ROMANIAN_ALPHABET,
    ALPHABET_SIZE,
    CHAR_TO_INDEX,
    INDEX_TO_CHAR,
    normalize_character,
    validate_key,
    validate_and_clean_text,
    validate_keyword,
)

from .caesar import (
    encrypt_caesar,
    decrypt_caesar,
    build_permuted_alphabet,
    encrypt_caesar_permuted,
    decrypt_caesar_permuted,
)

__all__ = [
    "ROMANIAN_ALPHABET",
    "ALPHABET_SIZE",
    "CHAR_TO_INDEX",
    "INDEX_TO_CHAR",
    "normalize_character",
    "validate_key",
    "validate_and_clean_text",
    "validate_keyword",
    "encrypt_caesar",
    "decrypt_caesar",
    "build_permuted_alphabet",
    "encrypt_caesar_permuted",
    "decrypt_caesar_permuted",
]
