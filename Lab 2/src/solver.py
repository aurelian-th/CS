"""Substitution cipher solver: substitution state tracker."""

import re
from typing import Dict, List, Optional, Tuple
from .corpus import ENGLISH_ALPHABET

# Verified ground truth mapping for Variant 2 (David Kahn: The Codebreakers)
# Ciphertext character (uppercase) -> Plaintext character (lowercase)
V2_GROUND_TRUTH_CIPHER_TO_PLAIN: Dict[str, str] = {
    "A": "b",
    "B": "q",
    "C": "f",
    "D": "u",
    "E": "j",
    "F": "y",
    "G": "n",
    "H": "c",
    "I": "r",
    "J": "g",
    "K": "v",
    "L": "k",
    "M": "z",
    "N": "o",
    "O": "d",
    "P": "s",
    "Q": "h",
    "R": "w",
    "S": "l",
    "T": "a",
    "U": "p",
    "V": "e",
    "W": "t",
    "X": "i",
    "Y": "x",
    "Z": "m",
}


class SubstitutionState:
    """Manages active substitution state between ciphertext and plaintext letters."""

    def __init__(self, initial_map: Optional[Dict[str, str]] = None):
        self.cipher_to_plain: Dict[str, str] = {}
        self.plain_to_cipher: Dict[str, str] = {}
        if initial_map:
            self.load_mapping(initial_map)

    def map_letter(self, cipher_char: str, plain_char: str) -> None:
        """Assign mapping: ciphertext char -> plaintext char."""
        c = cipher_char.upper()
        p = plain_char.lower()
        if c not in ENGLISH_ALPHABET or p.upper() not in ENGLISH_ALPHABET:
            raise ValueError(f"Invalid character pair: {cipher_char} -> {plain_char}")

        # If plain_char was mapped from another cipher char, clear previous
        if p in self.plain_to_cipher:
            old_c = self.plain_to_cipher[p]
            if old_c in self.cipher_to_plain:
                del self.cipher_to_plain[old_c]

        # If cipher_char already had a mapping, clear old plain_char reverse
        if c in self.cipher_to_plain:
            old_p = self.cipher_to_plain[c]
            if old_p in self.plain_to_cipher:
                del self.plain_to_cipher[old_p]

        self.cipher_to_plain[c] = p
        self.plain_to_cipher[p] = c

    def unmap_letter(self, cipher_char: str) -> None:
        """Remove mapping for given ciphertext character."""
        c = cipher_char.upper()
        if c in self.cipher_to_plain:
            p = self.cipher_to_plain[c]
            del self.cipher_to_plain[c]
            if p in self.plain_to_cipher:
                del self.plain_to_cipher[p]

    def swap_plain_letters(self, p1: str, p2: str) -> Tuple[bool, str]:
        """
        Swap the ciphertext letters that map to two plaintext letters.
        Example: swap 'b' and 'y' to fix 'secrecb' -> 'secrecy'.
        """
        p1_low, p2_low = p1.lower(), p2.lower()
        c1 = self.plain_to_cipher.get(p1_low)
        c2 = self.plain_to_cipher.get(p2_low)

        if not c1 and not c2:
            return False, f"Neither '{p1}' nor '{p2}' is currently mapped."
        if c1 and not c2:
            self.map_letter(c1, p2_low)
            return True, f"Reassigned {c1} -> {p2_low} (was -> {p1_low})"
        if c2 and not c1:
            self.map_letter(c2, p1_low)
            return True, f"Reassigned {c2} -> {p1_low} (was -> {p2_low})"

        # Both exist: swap them
        self.cipher_to_plain[c1] = p2_low
        self.cipher_to_plain[c2] = p1_low
        self.plain_to_cipher[p1_low] = c2
        self.plain_to_cipher[p2_low] = c1
        return True, f"Swapped: {c1} now maps to '{p2_low}', {c2} now maps to '{p1_low}'"

    def reset(self) -> None:
        """Clear all mappings."""
        self.cipher_to_plain.clear()
        self.plain_to_cipher.clear()

    def load_mapping(self, mapping: Dict[str, str]) -> None:
        """Load multiple mappings simultaneously."""
        self.reset()
        for c, p in mapping.items():
            self.map_letter(c, p)

    def is_complete(self) -> bool:
        """Check if all 26 letters have been mapped."""
        return len(self.cipher_to_plain) == 26

    def completion_percentage(self) -> float:
        """Percentage of the 26-letter alphabet currently mapped."""
        return (len(self.cipher_to_plain) / 26.0) * 100.0

    def decode_text(self, ciphertext: str, show_unmapped_as_upper: bool = True) -> str:
        """
        Translate ciphertext using current mapping.
        Decoded letters are rendered in lowercase; unmapped letters remain in uppercase ciphertext.
        """
        result = []
        for ch in ciphertext:
            if ch.isalpha():
                upper_ch = ch.upper()
                if upper_ch in self.cipher_to_plain:
                    p = self.cipher_to_plain[upper_ch]
                    result.append(p)
                else:
                    result.append(upper_ch if show_unmapped_as_upper else ch)
            else:
                result.append(ch)
        return "".join(result)

    def decode_clean_plaintext(self, ciphertext: str) -> str:
        """
        Decode text with standard grammatical capitalization preserved.
        Capitalizes initial sentence letters where applicable.
        """
        raw = self.decode_text(ciphertext, show_unmapped_as_upper=False)
        sentences = re.split(r"([.!?]\s+)", raw)
        capitalized = []
        for part in sentences:
            if part and part[0].isalpha():
                capitalized.append(part[0].upper() + part[1:])
            else:
                capitalized.append(part)
        return "".join(capitalized)

    def encode_text(self, plaintext: str) -> str:
        """Encode plaintext using the reverse mapping (plain -> cipher)."""
        result = []
        for ch in plaintext:
            if ch.isalpha():
                lower_ch = ch.lower()
                if lower_ch in self.plain_to_cipher:
                    c = self.plain_to_cipher[lower_ch]
                    result.append(c if ch.isupper() else c.lower())
                else:
                    result.append(ch)
            else:
                result.append(ch)
        return "".join(result)

    def get_mapping_table(self) -> List[Tuple[str, str]]:
        """Return list of (cipher_letter, plain_letter) sorted by cipher letter."""
        return [(c, self.cipher_to_plain.get(c, "-")) for c in ENGLISH_ALPHABET]
