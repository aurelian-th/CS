"""Playfair cipher implementation for Romanian messages using a 6x5 matrix."""

from typing import List, Tuple, Dict
from .alphabet import PLAYFAIR_ALPHABET, clean_text, validate_key


class PlayfairCipher:
    """Playfair cipher over a 6x5 matrix (30 Romanian letters, J merged into I)."""

    def __init__(self, key: str, rows: int = 6, cols: int = 5) -> None:
        self.rows = rows
        self.cols = cols
        self.key = validate_key(key)
        self.matrix, self.char_to_pos, self.pos_to_char = self._build_matrix(self.key)

    def _build_matrix(
        self, key: str
    ) -> Tuple[List[List[str]], Dict[str, Tuple[int, int]], Dict[Tuple[int, int], str]]:
        """Constructs the 6x5 key matrix from the keyword and remaining alphabet."""
        used = set()
        ordered = []

        # Add unique keyword letters (merging J into I)
        for raw_ch in key:
            ch = "I" if raw_ch == "J" else raw_ch
            if ch in PLAYFAIR_ALPHABET and ch not in used:
                used.add(ch)
                ordered.append(ch)

        # Add remaining alphabet letters
        for ch in PLAYFAIR_ALPHABET:
            if ch not in used:
                used.add(ch)
                ordered.append(ch)

        matrix: List[List[str]] = []
        char_to_pos: Dict[str, Tuple[int, int]] = {}
        pos_to_char: Dict[Tuple[int, int], str] = {}

        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                letter = ordered[r * self.cols + c]
                row.append(letter)
                char_to_pos[letter] = (r, c)
                pos_to_char[(r, c)] = letter
            matrix.append(row)

        char_to_pos["J"] = char_to_pos["I"]
        return matrix, char_to_pos, pos_to_char

    def format_matrix(self) -> str:
        """Returns the key matrix formatted as a clean grid."""
        lines = []
        header = "      " + "   ".join(f"c{c}" for c in range(self.cols))
        sep = "    " + "+---" * self.cols + "+"
        lines.append(header)
        lines.append(sep)

        for r in range(self.rows):
            row_str = " | ".join(f"{self.matrix[r][c]}" for c in range(self.cols))
            lines.append(f" r{r} | {row_str} |")
            lines.append(sep)

        return "\n".join(lines)

    def prepare_digraphs(self, text: str) -> List[Tuple[str, str]]:
        """Segments text into digraph pairs, inserting filler X between duplicate letters."""
        cleaned = clean_text(text).replace("J", "I")
        prepared: List[str] = []
        i = 0

        while i < len(cleaned):
            c1 = cleaned[i]
            if i + 1 < len(cleaned):
                c2 = cleaned[i + 1]
                if c1 == c2:
                    filler = "Z" if c1 == "X" else "X"
                    prepared.extend([c1, filler])
                    i += 1
                else:
                    prepared.extend([c1, c2])
                    i += 2
            else:
                filler = "Z" if c1 == "X" else "X"
                prepared.extend([c1, filler])
                i += 1

        return [(prepared[k], prepared[k + 1]) for k in range(0, len(prepared), 2)]

    def _transform_pair(self, c1: str, c2: str, mode: str) -> Tuple[str, str, str]:
        """Applies same row, same column, or rectangle transformation to a letter pair."""
        r1, col1 = self.char_to_pos[c1]
        r2, col2 = self.char_to_pos[c2]
        shift = 1 if mode == "encrypt" else -1

        if r1 == r2:
            rule = "Same row"
            out1 = self.pos_to_char[(r1, (col1 + shift) % self.cols)]
            out2 = self.pos_to_char[(r2, (col2 + shift) % self.cols)]
        elif col1 == col2:
            rule = "Same column"
            out1 = self.pos_to_char[((r1 + shift) % self.rows, col1)]
            out2 = self.pos_to_char[((r2 + shift) % self.rows, col2)]
        else:
            rule = "Rectangle"
            out1 = self.pos_to_char[(r1, col2)]
            out2 = self.pos_to_char[(r2, col1)]

        return out1, out2, rule

    def encrypt(self, plaintext: str) -> str:
        """Encrypts plaintext into a Playfair ciphertext."""
        pairs = self.prepare_digraphs(plaintext)
        result = []
        for c1, c2 in pairs:
            o1, o2, _ = self._transform_pair(c1, c2, mode="encrypt")
            result.extend([o1, o2])
        return "".join(result)

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts ciphertext into original digraphs."""
        cleaned = clean_text(ciphertext).replace("J", "I")
        if len(cleaned) % 2 != 0:
            raise ValueError(f"Ciphertext length must be even (received {len(cleaned)}).")

        pairs = [(cleaned[i], cleaned[i + 1]) for i in range(0, len(cleaned), 2)]
        result = []
        for c1, c2 in pairs:
            o1, o2, _ = self._transform_pair(c1, c2, mode="decrypt")
            result.extend([o1, o2])
        return "".join(result)

    def get_steps(self, text: str, mode: str = "encrypt") -> List[Dict[str, str]]:
        """Returns step traces for each transformed pair."""
        if mode == "encrypt":
            pairs = self.prepare_digraphs(text)
        else:
            cleaned = clean_text(text).replace("J", "I")
            pairs = [(cleaned[i], cleaned[i + 1]) for i in range(0, len(cleaned), 2)]

        steps = []
        for idx, (c1, c2) in enumerate(pairs, start=1):
            r1, col1 = self.char_to_pos[c1]
            r2, col2 = self.char_to_pos[c2]
            o1, o2, rule = self._transform_pair(c1, c2, mode=mode)
            steps.append({
                "index": str(idx),
                "in_pair": f"{c1}{c2}",
                "in_pos": f"({r1},{col1})-({r2},{col2})",
                "rule": rule,
                "out_pos": f"({self.char_to_pos[o1][0]},{self.char_to_pos[o1][1]})-({self.char_to_pos[o2][0]},{self.char_to_pos[o2][1]})",
                "out_pair": f"{o1}{o2}",
            })
        return steps
