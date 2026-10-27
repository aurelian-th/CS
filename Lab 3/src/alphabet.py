"""Romanian alphabet specification and character validation for the Playfair cipher."""

ROMANIAN_ALPHABET = (
    "A", "Ă", "Â", "B", "C", "D", "E", "F", "G", "H", "I", "Î", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "Ș", "T", "Ț", "U", "V", "W", "X", "Y", "Z",
)

PLAYFAIR_ALPHABET = tuple(ch for ch in ROMANIAN_ALPHABET if ch != "J")

_VALID_CHARS = set(ROMANIAN_ALPHABET)


def clean_text(raw_text: str) -> str:
    """Removes spaces, converts letters to uppercase, and validates the Romanian alphabet."""
    if not raw_text or not raw_text.strip():
        raise ValueError("Input text cannot be empty.")

    cleaned = []
    for ch in raw_text:
        if ch.isspace():
            continue
        upper = ch.upper()
        if upper not in _VALID_CHARS:
            raise ValueError(f"Invalid character '{ch}'. Only Romanian letters are allowed.")
        cleaned.append(upper)

    return "".join(cleaned)


def validate_key(raw_key: str, min_len: int = 7) -> str:
    """Validates encryption key length and character set."""
    key = clean_text(raw_key)
    if len(key) < min_len:
        raise ValueError(f"Key length must be at least {min_len} letters (received {len(key)}).")
    return key
