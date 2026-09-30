"""Caesar cipher implementation for the Romanian alphabet."""

from typing import List, Tuple, Dict
from .alphabet import (
    ROMANIAN_ALPHABET,
    ALPHABET_SIZE,
    CHAR_TO_INDEX,
    INDEX_TO_CHAR,
)


def encrypt_caesar(plaintext: str, key: int) -> str:
    """Encrypts plaintext with shift key k: c = (x + k) mod 31."""
    if key < 1 or key >= ALPHABET_SIZE:
        raise ValueError(f"Key k must be in range 1..{ALPHABET_SIZE - 1}, received {key}.")

    ciphertext_chars: List[str] = []
    for ch in plaintext:
        x = CHAR_TO_INDEX[ch]
        c_code = (x + key) % ALPHABET_SIZE
        ciphertext_chars.append(INDEX_TO_CHAR[c_code])

    return "".join(ciphertext_chars)


def decrypt_caesar(ciphertext: str, key: int) -> str:
    """Decrypts ciphertext with shift key k: m = (y - k) mod 31."""
    if key < 1 or key >= ALPHABET_SIZE:
        raise ValueError(f"Key k must be in range 1..{ALPHABET_SIZE - 1}, received {key}.")

    plaintext_chars: List[str] = []
    for ch in ciphertext:
        y = CHAR_TO_INDEX[ch]
        m_code = (y - key) % ALPHABET_SIZE
        plaintext_chars.append(INDEX_TO_CHAR[m_code])

    return "".join(plaintext_chars)


def build_permuted_alphabet(keyword: str) -> List[str]:
    """Constructs the permuted alphabet from keyword k2 followed by remaining letters."""
    seen = set()
    permuted: List[str] = []

    for ch in keyword:
        if ch not in seen and ch in CHAR_TO_INDEX:
            seen.add(ch)
            permuted.append(ch)

    for ch in ROMANIAN_ALPHABET:
        if ch not in seen:
            seen.add(ch)
            permuted.append(ch)

    return permuted


def encrypt_caesar_permuted(
    plaintext: str, key1: int, keyword: str
) -> Tuple[str, List[str]]:
    """Encrypts plaintext using shift key k1 and permuted alphabet from keyword k2."""
    if key1 < 1 or key1 >= ALPHABET_SIZE:
        raise ValueError(f"Key k1 must be in range 1..{ALPHABET_SIZE - 1}, received {key1}.")

    permuted_alphabet = build_permuted_alphabet(keyword)
    perm_char_to_index: Dict[str, int] = {ch: idx for idx, ch in enumerate(permuted_alphabet)}

    ciphertext_chars: List[str] = []
    for ch in plaintext:
        x = perm_char_to_index[ch]
        c_code = (x + key1) % ALPHABET_SIZE
        ciphertext_chars.append(permuted_alphabet[c_code])

    return "".join(ciphertext_chars), permuted_alphabet


def decrypt_caesar_permuted(
    ciphertext: str, key1: int, keyword: str
) -> Tuple[str, List[str]]:
    """Decrypts ciphertext using shift key k1 and permuted alphabet from keyword k2."""
    if key1 < 1 or key1 >= ALPHABET_SIZE:
        raise ValueError(f"Key k1 must be in range 1..{ALPHABET_SIZE - 1}, received {key1}.")

    permuted_alphabet = build_permuted_alphabet(keyword)
    perm_char_to_index: Dict[str, int] = {ch: idx for idx, ch in enumerate(permuted_alphabet)}

    plaintext_chars: List[str] = []
    for ch in ciphertext:
        y = perm_char_to_index[ch]
        m_code = (y - key1) % ALPHABET_SIZE
        plaintext_chars.append(permuted_alphabet[m_code])

    return "".join(plaintext_chars), permuted_alphabet
