"""Comprehensive unit test suite for Monoalphabetic Cryptanalysis Suite."""

import pytest
import sys
import os

# Add package root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus import (
    ENGLISH_ALPHABET,
    ENGLISH_UNIGRAM_FREQS,
    ENGLISH_IC,
    RANDOM_IC,
)
from src.analyzer import (
    calculate_unigram_frequencies,
    calculate_relative_frequencies,
    calculate_index_of_coincidence,
    calculate_chi_squared,
    extract_ngrams,
    extract_doubles,
    extract_single_letter_words,
    filter_letters_only,
)
from src.variants import (
    get_variant,
    resolve_variant_number,
    list_available_variants,
    TOTAL_ASSIGNMENT_VARIANTS,
)
from src.solver import (
    SubstitutionState,
    GuidedSolver,
    AutomatedSolver,
    V2_GROUND_TRUTH_CIPHER_TO_PLAIN,
)


class TestLinguisticAnalyzer:
    """Tests for statistical analysis functions."""

    def test_filter_letters_only(self):
        sample = "The addition of secrecy, 1920! #cryptography"
        filtered = filter_letters_only(sample)
        assert filtered.isalpha()
        assert filtered == "THEADDITIONOFSECRECYCRYPTOGRAPHY"

    def test_unigram_frequencies_sum(self):
        text, _, _ = get_variant(2)
        raw_counts = calculate_unigram_frequencies(text)
        assert len(raw_counts) == 26
        total_counted = sum(raw_counts.values())
        actual_letters = sum(1 for c in text if c.isalpha())
        assert total_counted == actual_letters

    def test_relative_frequencies_sum(self):
        text, _, _ = get_variant(2)
        rel = calculate_relative_frequencies(text)
        assert len(rel) == 26
        assert pytest.approx(sum(rel.values()), rel=1e-3) == 100.0

    def test_index_of_coincidence_variant2(self):
        text, _, _ = get_variant(2)
        ic = calculate_index_of_coincidence(text)
        # English prose typically falls between 0.063 and 0.069
        assert 0.060 <= ic <= 0.070
        assert ic > 0.050  # Must be significantly higher than random (0.0385)

    def test_index_of_coincidence_empty(self):
        assert calculate_index_of_coincidence("") == 0.0
        assert calculate_index_of_coincidence("A") == 0.0

    def test_chi_squared_identical_distribution(self):
        # A synthetic text having identical distribution to English should yield chi^2 ~ 0
        chi = calculate_chi_squared("EEEEEEEEEEEEEEEE", {"E": 100.0, **{c: 0.0 for c in ENGLISH_ALPHABET if c != "E"}})
        assert chi == 0.0

    def test_ngrams_extraction(self):
        sample = "THE THREE MEN WENT TO THE THEATER"
        bigrams = dict(extract_ngrams(sample, n=2))
        assert bigrams["TH"] >= 4
        assert bigrams["HE"] >= 3

        trigrams = dict(extract_ngrams(sample, n=3))
        assert trigrams["THE"] >= 3


class TestVariantManager:
    """Tests for variant resolution and loading."""

    def test_variant_25_modulo_mapping(self):
        resolved, note = resolve_variant_number(25)
        # Formula: ((25 - 1) % 23) + 1 = (24 % 23) + 1 = 1 + 1 = 2
        assert resolved == 2
        assert "Variant 25 resolved to Variant 2" in note

    def test_variant_boundary_conditions(self):
        assert resolve_variant_number(1)[0] == 1
        assert resolve_variant_number(23)[0] == 23
        assert resolve_variant_number(24)[0] == 1
        assert resolve_variant_number(46)[0] == 23
        assert resolve_variant_number(47)[0] == 1

    def test_invalid_variant_numbers(self):
        with pytest.raises(ValueError):
            resolve_variant_number(0)
        with pytest.raises(ValueError):
            resolve_variant_number(-5)

    def test_all_variants_exist(self):
        available = list_available_variants()
        assert len(available) == TOTAL_ASSIGNMENT_VARIANTS
        assert available == list(range(1, 24))

    def test_variant_retrieval_default(self):
        # Default should retrieve student variant 25 -> resolved to 2
        text, v_id, note = get_variant(25)
        assert v_id == 2
        assert len(text) > 1000
        assert text.startswith("Wqv tooxwxng nc pvhivhf")


class TestSubstitutionState:
    """Tests for the substitution state machine and decoder."""

    def test_letter_mapping_and_unmapping(self):
        state = SubstitutionState()
        state.map_letter("W", "t")
        assert state.cipher_to_plain["W"] == "t"
        assert state.plain_to_cipher["t"] == "W"

        state.unmap_letter("W")
        assert "W" not in state.cipher_to_plain
        assert "t" not in state.plain_to_cipher

    def test_bijection_preservation(self):
        # Assigning another cipher letter to same plain letter should unmap the old one
        state = SubstitutionState()
        state.map_letter("W", "t")
        state.map_letter("K", "t")
        assert state.cipher_to_plain["K"] == "t"
        assert "W" not in state.cipher_to_plain
        assert state.plain_to_cipher["t"] == "K"

    def test_decode_with_partial_mapping(self):
        state = SubstitutionState({"W": "t", "Q": "h", "V": "e"})
        cipher = "Wqv tooxwxng nc pvhivhf"
        decoded = state.decode_text(cipher)
        # Mapped letters are lowercase ('t', 'h', 'e'), unmapped are uppercase
        assert decoded.startswith("the TOOXtXNG NC PeHIeHF")

    def test_punctuation_and_whitespace_preservation(self):
        state = SubstitutionState(V2_GROUND_TRUTH_CIPHER_TO_PLAIN)
        cipher = "Wqv tooxwxng, 1920—tgo 'Vjfuw'p'!"
        decoded = state.decode_text(cipher)
        assert "," in decoded
        assert "1920" in decoded
        assert "—" in decoded
        assert "'egypt's'!" in decoded.lower()

    def test_v2_ground_truth_decryption(self):
        text, _, _ = get_variant(2)
        state = SubstitutionState(V2_GROUND_TRUTH_CIPHER_TO_PLAIN)
        assert state.is_complete()
        assert state.completion_percentage() == 100.0

        plaintext = state.decode_clean_plaintext(text)
        assert "The addition of secrecy to the transformations producedcryptography." in plaintext
        assert "True, it was more of a" in plaintext
        assert "Egypt's wasthus a" in plaintext
        assert "quasi cryptology" in plaintext
        assert "Wu-ching tsung-yao" in plaintext or "wu-ching tsung-yao" in plaintext.lower()


class TestGuidedSolver:
    """Tests for the step-by-step pedagogical walkthrough."""

    def test_guided_steps_progression(self):
        text, _, _ = get_variant(2)
        solver = GuidedSolver(text)
        steps = solver.generate_steps()

        assert len(steps) == 6
        assert steps[0].step_number == 1
        assert "WQV" in steps[0].title
        assert len(steps[0].cumulative_mappings) == 3

        # Step 6 must map all 26 letters
        assert steps[5].step_number == 6
        assert len(steps[5].cumulative_mappings) == 26

        # Step 6 decoded sample must contain 'cryptography'
        assert "cryptography" in steps[5].preview_decryption.lower()


class TestAutomatedSolver:
    """Tests for the stochastic hill-climbing solver."""

    def test_automated_solver_score_improvement(self):
        text, _, _ = get_variant(2)
        auto = AutomatedSolver(text)
        initial_key = auto.generate_initial_key()
        initial_score = auto.score_key(initial_key)

        best_key, best_score, _ = auto.solve(max_iterations=1200, restarts=2, seed=123)
        assert best_score > initial_score
        assert len(best_key) == 26
