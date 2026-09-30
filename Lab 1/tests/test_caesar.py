"""Unit and integration test suite for Romanian Caesar cipher."""

import unittest
import sys
import os

# Ensure package root is in sys.path for test discovery
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.alphabet import (
    ROMANIAN_ALPHABET,
    ALPHABET_SIZE,
    CHAR_TO_INDEX,
    INDEX_TO_CHAR,
    normalize_character,
    validate_key,
    validate_and_clean_text,
    validate_keyword,
)
from src.caesar import (
    encrypt_caesar,
    decrypt_caesar,
    build_permuted_alphabet,
    encrypt_caesar_permuted,
    decrypt_caesar_permuted,
)


class TestRomanianAlphabetEncoding(unittest.TestCase):
    """Verifies compliance with Table 2 of the laboratory assignment."""

    def test_alphabet_length(self):
        self.assertEqual(len(ROMANIAN_ALPHABET), 31)
        self.assertEqual(ALPHABET_SIZE, 31)

    def test_table_2_positions(self):
        self.assertEqual(ROMANIAN_ALPHABET[0], "A")
        self.assertEqual(ROMANIAN_ALPHABET[1], "Ă")
        self.assertEqual(ROMANIAN_ALPHABET[2], "Â")
        self.assertEqual(ROMANIAN_ALPHABET[3], "B")
        self.assertEqual(ROMANIAN_ALPHABET[10], "I")
        self.assertEqual(ROMANIAN_ALPHABET[11], "Î")
        self.assertEqual(ROMANIAN_ALPHABET[21], "S")
        self.assertEqual(ROMANIAN_ALPHABET[22], "Ș")
        self.assertEqual(ROMANIAN_ALPHABET[23], "T")
        self.assertEqual(ROMANIAN_ALPHABET[24], "Ț")
        self.assertEqual(ROMANIAN_ALPHABET[30], "Z")

    def test_bidirectional_mapping(self):
        for idx, char in enumerate(ROMANIAN_ALPHABET):
            self.assertEqual(CHAR_TO_INDEX[char], idx)
            self.assertEqual(INDEX_TO_CHAR[idx], char)

    def test_cedilla_normalization(self):
        self.assertEqual(normalize_character("Ş"), "Ș")
        self.assertEqual(normalize_character("ş"), "Ș")
        self.assertEqual(normalize_character("Ţ"), "Ț")
        self.assertEqual(normalize_character("ţ"), "Ț")
        self.assertEqual(normalize_character("ă"), "Ă")
        self.assertEqual(normalize_character("â"), "Â")
        self.assertEqual(normalize_character("î"), "Î")


class TestInputValidation(unittest.TestCase):
    """Verifies input validation rules and error diagnostic messaging."""

    def test_key_validation_valid(self):
        for k in range(1, 31):
            is_valid, parsed_k, err = validate_key(k)
            self.assertTrue(is_valid)
            self.assertEqual(parsed_k, k)
            self.assertIsNone(err)

            is_valid_str, parsed_k_str, _ = validate_key(str(k))
            self.assertTrue(is_valid_str)
            self.assertEqual(parsed_k_str, k)

    def test_key_validation_invalid_bounds(self):
        is_valid, _, err = validate_key(0)
        self.assertFalse(is_valid)
        self.assertIn("between 1 and 30", err)

        is_valid, _, err = validate_key(31)
        self.assertFalse(is_valid)
        self.assertIn("between 1 and 30", err)

        is_valid, _, err = validate_key(-5)
        self.assertFalse(is_valid)
        self.assertIn("between 1 and 30", err)

        is_valid, _, err = validate_key("abc")
        self.assertFalse(is_valid)
        self.assertIn("valid integer", err)

    def test_text_validation_valid(self):
        raw_valid = "Cifrul Cezar cu diacritice şcoală şi ţară"
        is_valid, cleaned, err = validate_and_clean_text(raw_valid)
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        expected = "CIFRULCEZARCUDIACRITICEȘCOALĂȘIȚARĂ"
        self.assertEqual(cleaned, expected)

    def test_text_validation_rejection_details(self):
        is_valid, _, err = validate_and_clean_text("Cezar 2026")
        self.assertFalse(is_valid)
        self.assertIn("rejected character '2'", err)
        self.assertIn("position 7", err)

        is_valid, _, err = validate_and_clean_text("Salut!")
        self.assertFalse(is_valid)
        self.assertIn("rejected character '!'", err)
        self.assertIn("position 6", err)

        is_valid, _, err = validate_and_clean_text("   ")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", err)

    def test_keyword_validation(self):
        is_valid, cleaned, err = validate_keyword("criptografie")
        self.assertTrue(is_valid)
        self.assertEqual(cleaned, "CRIPTOGRAFIE")

        is_valid, cleaned, _ = validate_keyword("informaţional")
        self.assertTrue(is_valid)
        self.assertEqual(cleaned, "INFORMAȚIONAL")

        is_valid, _, err = validate_keyword("scurt")
        self.assertFalse(is_valid)
        self.assertIn("at least 7 characters", err)

        is_valid, _, err = validate_keyword("parola123")
        self.assertFalse(is_valid)
        self.assertIn("rejected character '1'", err)


class TestTask1_1CaesarCipher(unittest.TestCase):
    """Verifies Task 1.1 single-key Caesar cipher operations."""

    def test_romanian_table_2_shift_k3(self):
        plaintext = "CIFRULCEZAR"
        expected_cipher = "FKITXOFHÂBT"
        cipher = encrypt_caesar(plaintext, 3)
        self.assertEqual(cipher, expected_cipher)

        decrypted = decrypt_caesar(cipher, 3)
        self.assertEqual(decrypted, plaintext)

    def test_round_trip_all_keys(self):
        text = "ACESTAESTEUNTEXTDETESTPENTRUCIFRULCEZAR"
        for k in range(1, 31):
            cipher = encrypt_caesar(text, k)
            dec = decrypt_caesar(cipher, k)
            self.assertEqual(dec, text, f"Round trip failed for key k={k}")

    def test_wrap_around_boundaries(self):
        self.assertEqual(encrypt_caesar("Z", 1), "A")
        self.assertEqual(decrypt_caesar("A", 1), "Z")
        self.assertEqual(encrypt_caesar("Z", 30), "Y")
        self.assertEqual(decrypt_caesar("Y", 30), "Z")


class TestTask1_2PermutedCaesarCipher(unittest.TestCase):
    """Verifies Task 1.2 two-key Caesar cipher with alphabet permutation."""

    def test_build_permuted_alphabet_uniqueness_and_length(self):
        keyword = "CRIPTOGRAFIE"
        perm = build_permuted_alphabet(keyword)
        self.assertEqual(len(perm), 31)
        self.assertEqual(len(set(perm)), 31)

        expected_prefix = ["C", "R", "I", "P", "T", "O", "G", "A", "F", "E"]
        self.assertEqual(perm[:10], expected_prefix)

        expected_suffix = [
            "Ă", "Â", "B", "D", "H", "Î", "J", "K", "L", "M", "N",
            "Q", "S", "Ș", "Ț", "U", "V", "W", "X", "Y", "Z"
        ]
        self.assertEqual(perm[10:], expected_suffix)

    def test_two_key_round_trip(self):
        keywords = ["CRIPTOGRAFIE", "SECURITATEA", "ALGORITMICA", "UNIVERSITATE"]
        plaintext = "ANALIZACRIPTOGRAFICAAPROGRAMULUI"

        for kw in keywords:
            for k1 in [1, 3, 7, 15, 30]:
                cipher, perm = encrypt_caesar_permuted(plaintext, k1, kw)
                self.assertEqual(len(perm), 31)
                dec, _ = decrypt_caesar_permuted(cipher, k1, kw)
                self.assertEqual(dec, plaintext, f"Failed for keyword={kw}, k1={k1}")


class TestDatasetVectors(unittest.TestCase):
    """Loads and validates all vectors from data/test_vectors.json."""

    def test_json_test_vectors(self):
        import json
        vector_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "test_vectors.json",
        )
        with open(vector_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for v in data["task_1_1_vectors"]:
            with self.subTest(vector_id=v["id"]):
                c = encrypt_caesar(v["cleaned_plaintext"], v["key"])
                self.assertEqual(c, v["expected_ciphertext"])
                m = decrypt_caesar(c, v["key"])
                self.assertEqual(m, v["cleaned_plaintext"])

        for v in data["task_1_2_vectors"]:
            with self.subTest(vector_id=v["id"]):
                c, perm = encrypt_caesar_permuted(
                    v["cleaned_plaintext"], v["key1"], v["keyword_k2"]
                )
                self.assertEqual("".join(perm), v["permuted_alphabet"])
                self.assertEqual(c, v["expected_ciphertext"])
                m, _ = decrypt_caesar_permuted(c, v["key1"], v["keyword_k2"])
                self.assertEqual(m, v["cleaned_plaintext"])


if __name__ == "__main__":
    unittest.main()
