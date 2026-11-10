"""Core key schedule generation engine for the Data Encryption Standard (DES).

Implements Permuted Choice 1 (PC-1), 28-bit circular left shifts per round,
and Permuted Choice 2 (PC-2) to produce 48-bit round keys (Ki) from 56-bit K+.
"""

import secrets
from dataclasses import dataclass
from typing import List, Tuple

from .tables import PC1_C, PC1_D, PC2, ROUND_SHIFTS


@dataclass(frozen=True)
class RoundStep:
    """Represents intermediate state and outputs for a single DES key schedule round."""

    round_number: int
    shift: int
    c_prev: str
    d_prev: str
    c_curr: str
    d_curr: str
    cd_curr: str
    round_key: str

    @property
    def c_hex(self) -> str:
        """Hexadecimal representation of 28-bit register C."""
        return bin_to_hex(self.c_curr, 7)

    @property
    def d_hex(self) -> str:
        """Hexadecimal representation of 28-bit register D."""
        return bin_to_hex(self.d_curr, 7)

    @property
    def cd_hex(self) -> str:
        """Hexadecimal representation of 56-bit concatenated registers CD."""
        return bin_to_hex(self.cd_curr, 14)

    @property
    def key_hex(self) -> str:
        """Hexadecimal representation of 48-bit round key Ki."""
        return bin_to_hex(self.round_key, 12)

    @property
    def key_blocks_6bit(self) -> List[str]:
        """48-bit round key partitioned into 8 six-bit blocks (B1 to B8)."""
        return [self.round_key[i : i + 6] for i in range(0, 48, 6)]


def bin_to_hex(bin_str: str, hex_len: int) -> str:
    """Converts a binary string to uppercase hexadecimal padded to hex_len characters."""
    val = int(bin_str, 2)
    return f"{val:0{hex_len}X}"


def hex_to_bin(hex_str: str, expected_bits: int) -> str:
    """Converts a hexadecimal string to binary string padded to expected_bits."""
    val = int(hex_str, 16)
    return bin(val)[2:].zfill(expected_bits)


def left_rotate(bits: str, shift: int) -> str:
    """Performs circular left shift on a bit string."""
    shift = shift % len(bits)
    return bits[shift:] + bits[:shift]


def validate_and_parse_k_plus(raw_input: str) -> str:
    """Validates and parses K+ input from hexadecimal (14 chars) or binary (56 chars)."""
    clean = "".join(raw_input.split())
    if not clean:
        raise ValueError("Key K+ cannot be empty.")

    if len(clean) == 56 and all(ch in "01" for ch in clean):
        return clean

    if len(clean) == 14:
        try:
            return hex_to_bin(clean, 56)
        except ValueError as exc:
            raise ValueError(f"Invalid hexadecimal string '{clean}'.") from exc

    raise ValueError(
        f"Input must be either 14 hexadecimal characters or 56 binary digits (received {len(clean)} characters)."
    )


def validate_and_parse_64bit_key(raw_input: str) -> str:
    """Validates and parses a 64-bit key from 8 ASCII characters, 16 hex digits, or 64 binary digits."""
    clean = raw_input.strip()
    if not clean:
        raise ValueError("Key cannot be empty.")

    # 64 binary bits
    no_spaces = "".join(clean.split())
    if len(no_spaces) == 64 and all(ch in "01" for ch in no_spaces):
        return no_spaces

    # 16 hex digits
    if len(no_spaces) == 16:
        try:
            return hex_to_bin(no_spaces, 64)
        except ValueError:
            pass

    # 8 ASCII characters
    if len(clean) == 8:
        return "".join(bin(ord(ch))[2:].zfill(8) for ch in clean)

    raise ValueError(
        f"Input must be 8 ASCII characters, 16 hexadecimal digits, or 64 binary digits (received {len(clean)} characters)."
    )


def apply_pc1(key_64_bin: str) -> Tuple[str, str, str]:
    """Applies Permuted Choice 1 (PC-1) to a 64-bit key, returning (K+, C0, D0)."""
    if len(key_64_bin) != 64:
        raise ValueError(f"64-bit key must be exactly 64 bits (received {len(key_64_bin)}).")

    c0 = "".join(key_64_bin[pos - 1] for pos in PC1_C)
    d0 = "".join(key_64_bin[pos - 1] for pos in PC1_D)
    k_plus = c0 + d0
    return k_plus, c0, d0


def apply_pc2(cd_56_bin: str) -> str:
    """Applies Permuted Choice 2 (PC-2) to 56-bit (Ci || Di) returning 48-bit Ki."""
    if len(cd_56_bin) != 56:
        raise ValueError(f"PC-2 input must be exactly 56 bits (received {len(cd_56_bin)}).")

    return "".join(cd_56_bin[pos - 1] for pos in PC2)


def generate_random_k_plus() -> str:
    """Generates a cryptographically random 56-bit K+ binary string."""
    random_int = secrets.randbits(56)
    return bin(random_int)[2:].zfill(56)


def generate_random_64bit_key_hex() -> str:
    """Generates a cryptographically random 64-bit key represented as 16 hex digits."""
    random_int = secrets.randbits(64)
    return f"{random_int:016X}"


class DESKeySchedule:
    """Manages state and transformations for the DES round key schedule."""

    def __init__(self, k_plus_bin: str) -> None:
        if len(k_plus_bin) != 56 or not all(ch in "01" for ch in k_plus_bin):
            raise ValueError("K+ must be a 56-bit binary string.")
        self.k_plus = k_plus_bin
        self.c0 = k_plus_bin[:28]
        self.d0 = k_plus_bin[28:]
        self._steps: List[RoundStep] = self._compute_all_steps()

    @classmethod
    def from_k_plus(cls, raw_input: str) -> "DESKeySchedule":
        """Instantiates schedule from hex or binary K+ input."""
        k_plus_bin = validate_and_parse_k_plus(raw_input)
        return cls(k_plus_bin)

    @classmethod
    def from_64bit_key(cls, raw_input: str) -> Tuple["DESKeySchedule", str]:
        """Instantiates schedule from 64-bit key and returns (schedule, 64_bit_bin)."""
        key_64_bin = validate_and_parse_64bit_key(raw_input)
        k_plus_bin, _, _ = apply_pc1(key_64_bin)
        return cls(k_plus_bin), key_64_bin

    def _compute_all_steps(self) -> List[RoundStep]:
        """Precomputes all 16 rounds of the key schedule."""
        steps: List[RoundStep] = []
        c_curr, d_curr = self.c0, self.d0

        for idx, shift in enumerate(ROUND_SHIFTS, start=1):
            c_prev, d_prev = c_curr, d_curr
            c_curr = left_rotate(c_prev, shift)
            d_curr = left_rotate(d_prev, shift)
            cd_curr = c_curr + d_curr
            round_key = apply_pc2(cd_curr)

            steps.append(
                RoundStep(
                    round_number=idx,
                    shift=shift,
                    c_prev=c_prev,
                    d_prev=d_prev,
                    c_curr=c_curr,
                    d_curr=d_curr,
                    cd_curr=cd_curr,
                    round_key=round_key,
                )
            )

        return steps

    def get_round(self, round_num: int) -> RoundStep:
        """Retrieves step information for a given round number (1 to 16)."""
        if not (1 <= round_num <= 16):
            raise ValueError(f"Round number must be between 1 and 16 (received {round_num}).")
        return self._steps[round_num - 1]

    def get_all_rounds(self) -> List[RoundStep]:
        """Retrieves all 16 round steps."""
        return list(self._steps)

    @staticmethod
    def format_pc1_table() -> str:
        """Formats Permuted Choice 1 (PC-1) table as clean text."""
        lines = [
            "Permuted choice 1 (PC-1): 56 bits selected from 64-bit key (parity bits discarded)",
            "",
            "  Left register C0 (28 bits):",
        ]
        for row in range(4):
            chunk = PC1_C[row * 7 : (row + 1) * 7]
            lines.append("    " + "  ".join(f"{pos:2d}" for pos in chunk))
        lines.append("")
        lines.append("  Right register D0 (28 bits):")
        for row in range(4):
            chunk = PC1_D[row * 7 : (row + 1) * 7]
            lines.append("    " + "  ".join(f"{pos:2d}" for pos in chunk))
        return "\n".join(lines)

    @staticmethod
    def format_pc2_table() -> str:
        """Formats Permuted Choice 2 (PC-2) table as clean text."""
        lines = [
            "Permuted choice 2 (PC-2): 48 bits selected from 56-bit (Ci || Di)",
            "  Omitted bit indices: 9, 18, 22, 25, 35, 38, 43, 54",
            "",
        ]
        for row in range(8):
            chunk = PC2[row * 6 : (row + 1) * 6]
            lines.append("    " + "  ".join(f"{pos:2d}" for pos in chunk))
        return "\n".join(lines)

    @staticmethod
    def format_shift_schedule() -> str:
        """Formats round left circular shift schedule."""
        lines = [
            "Round left circular shift schedule (total shifts = 28):",
            "  Round  | 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16",
            "  Shift  | 1  1  2  2  2  2  2  2  1  2  2  2  2  2  2  1",
        ]
        return "\n".join(lines)
