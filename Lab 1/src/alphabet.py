"""Romanian alphabet specification and character validation."""

from typing import Tuple, Optional, Dict, List

# Romanian alphabet for Laboratory Work 1 (Table 2, n = 31)
ROMANIAN_ALPHABET: Tuple[str, ...] = (
    "A",  # 0
    "Ă",  # 1
    "Â",  # 2
    "B",  # 3
    "C",  # 4
    "D",  # 5
    "E",  # 6
    "F",  # 7
    "G",  # 8
    "H",  # 9
    "I",  # 10
    "Î",  # 11
    "J",  # 12
    "K",  # 13
    "L",  # 14
    "M",  # 15
    "N",  # 16
    "O",  # 17
    "P",  # 18
    "Q",  # 19
    "R",  # 20
    "S",  # 21
    "Ș",  # 22
    "T",  # 23
    "Ț",  # 24
    "U",  # 25
    "V",  # 26
    "W",  # 27
    "X",  # 28
    "Y",  # 29
    "Z",  # 30
)

ALPHABET_SIZE: int = len(ROMANIAN_ALPHABET)

# Table 2 mappings
CHAR_TO_INDEX: Dict[str, int] = {char: idx for idx, char in enumerate(ROMANIAN_ALPHABET)}
INDEX_TO_CHAR: Dict[int, str] = {idx: char for idx, char in enumerate(ROMANIAN_ALPHABET)}

# Cedilla to comma-below normalization map
CEDILLA_NORMALIZATION_MAP: Dict[str, str] = {
    "Ş": "Ș",
    "ş": "Ș",
    "Ţ": "Ț",
    "ţ": "Ț",
}

VALID_ROMANIAN_CHARS = set(ROMANIAN_ALPHABET)


def normalize_character(ch: str) -> str:
    """Normalizes cedillas to standard comma-below diacritics and converts to uppercase."""
    if ch in CEDILLA_NORMALIZATION_MAP:
        return CEDILLA_NORMALIZATION_MAP[ch]
    return ch.upper()


def validate_key(key_input: str | int) -> Tuple[bool, int, Optional[str]]:
    """Validates that shift key k is an integer between 1 and 30 inclusive."""
    try:
        k = int(str(key_input).strip())
    except (ValueError, TypeError):
        return False, 0, f"key must be a valid integer between 1 and 30 (received '{key_input}')."

    if k < 1 or k > (ALPHABET_SIZE - 1):
        return False, 0, f"key must be an integer between 1 and 30 inclusive (received {k})."

    return True, k, None


def validate_and_clean_text(raw_text: str) -> Tuple[bool, str, Optional[str]]:
    """Validates text against Romanian alphabet, removes spaces, and normalizes characters."""
    if raw_text is None:
        return False, "", "input text cannot be empty."

    cleaned_chars: List[str] = []
    for pos, ch in enumerate(raw_text, start=1):
        if ch.isspace():
            continue

        norm_ch = normalize_character(ch)
        if norm_ch in VALID_ROMANIAN_CHARS:
            cleaned_chars.append(norm_ch)
        else:
            return (
                False,
                "",
                f"rejected character '{ch}' at position {pos}. Only Romanian letters and spaces are allowed.",
            )

    cleaned_text = "".join(cleaned_chars)
    if not cleaned_text:
        return False, "", "input text cannot be empty."

    return True, cleaned_text, None


def validate_keyword(raw_keyword: str) -> Tuple[bool, str, Optional[str]]:
    """Validates keyword k2: must contain only Romanian letters and length >= 7."""
    if raw_keyword is None:
        return False, "", "keyword cannot be empty."

    is_valid, cleaned, error = validate_and_clean_text(raw_keyword)
    if not is_valid:
        return False, "", error

    if len(cleaned) < 7:
        return False, "", f"keyword must be at least 7 characters (received {len(cleaned)})."

    return True, cleaned, None
