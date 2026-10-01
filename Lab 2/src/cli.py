#!/usr/bin/env python3
"""Command-line interface and interactive cryptanalysis suite for monoalphabetic ciphers."""

import sys
import os
import argparse
from typing import Dict, List, Optional, Tuple

# Ensure package root is in sys.path when executed directly
if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.corpus import (
        ENGLISH_ALPHABET,
        ENGLISH_UNIGRAM_FREQS,
        ENGLISH_IC,
        RANDOM_IC,
        TOP_BIGRAMS,
        TOP_TRIGRAMS,
    )
    from src.analyzer import (
        calculate_unigram_frequencies,
        calculate_relative_frequencies,
        calculate_index_of_coincidence,
        calculate_chi_squared,
        extract_ngrams,
        extract_doubles,
        extract_single_letter_words,
        get_sorted_unigrams,
    )
    from src.variants import (
        get_variant,
        resolve_variant_number,
        list_available_variants,
        TOTAL_ASSIGNMENT_VARIANTS,
    )
    from src.solver import (
        SubstitutionState,
        AutomatedSolver,
        V2_GROUND_TRUTH_CIPHER_TO_PLAIN,
    )
else:
    from .corpus import (
        ENGLISH_ALPHABET,
        ENGLISH_UNIGRAM_FREQS,
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
        get_sorted_unigrams,
    )
    from .variants import (
        get_variant,
        resolve_variant_number,
        list_available_variants,
        TOTAL_ASSIGNMENT_VARIANTS,
    )
    from .solver import (
        SubstitutionState,
        AutomatedSolver,
        V2_GROUND_TRUTH_CIPHER_TO_PLAIN,
    )


def print_frequency_table(text: str) -> None:
    """Print tabular frequency analysis compared with standard English."""
    unigrams = get_sorted_unigrams(text)
    total_letters = sum(cnt for _, cnt, _ in unigrams)

    print(f"\nLetter frequency analysis (total letters: {total_letters}):")
    print(f"{'Cipher':<8}{'Count':<8}{'Observed %':<14}{'English Ref %':<16}{'Difference':<12}")
    print("-" * 58)

    for char, cnt, pct in unigrams:
        ref_pct = ENGLISH_UNIGRAM_FREQS.get(char, 0.0)
        diff = pct - ref_pct
        sign = "+" if diff > 0 else ""
        print(f"{char:<8}{cnt:<8}{pct:>6.2f}%       {ref_pct:>6.2f}%         {sign}{diff:>5.2f}%")
    print()


def print_ngrams_table(text: str, top_n: int = 10) -> None:
    """Print top bigrams and trigrams."""
    bigrams = extract_ngrams(text, n=2)[:top_n]
    trigrams = extract_ngrams(text, n=3)[:top_n]
    doubles = extract_doubles(text)[:top_n]
    singles = extract_single_letter_words(text)

    print(f"\nTop {top_n} bigrams:")
    for bg, cnt in bigrams:
        print(f"  {bg}: {cnt}")

    print(f"\nTop {top_n} trigrams:")
    for tg, cnt in trigrams:
        print(f"  {tg}: {cnt}")

    if doubles:
        print("\nDoubled letters:")
        for db, cnt in doubles:
            print(f"  {db}: {cnt}")

    if singles:
        print("\nSingle-letter tokens:")
        for s, cnt in singles:
            print(f"  '{s}': {cnt}")
    print()


def print_key_table(state: SubstitutionState) -> None:
    """Display the substitution mapping table in 2-row layout."""
    table = state.get_mapping_table()
    cipher_row = "  ".join(f"{c:>2}" for c, _ in table)
    plain_row = "  ".join(f"{p:>2}" for _, p in table)

    print("\nSubstitution key mapping:")
    print(f"  Cipher: {cipher_row}")
    print(f"  Plain:  {plain_row}")
    mapped_count = len(state.cipher_to_plain)
    print(f"  Mapped: {mapped_count}/26 letters ({state.completion_percentage():.1f}%)\n")


def run_interactive_sandbox(ciphertext: str, state: SubstitutionState) -> None:
    """Interactive loop allowing manual letter mapping and real-time decoded preview."""
    print("\nInteractive substitution sandbox")
    print("Commands:")
    print("  m <C> <P>     : Map cipher letter C to plain letter P (e.g. 'm w t')")
    print("  u <C>         : Unmap cipher letter C (e.g. 'u w')")
    print("  swap <P1> <P2>: Swap two plaintext letters (e.g. 'swap b y' to fix 'secrecb')")
    print("  auto          : Run automated hill-climbing solver")
    print("  key           : Display current substitution table")
    print("  text          : Display decoded text with current mapping")
    print("  solve         : Load verified ground truth key")
    print("  reset         : Clear all letter mappings")
    print("  b             : Back to main menu\n")

    while True:
        try:
            line = input("sandbox> ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ("b", "back", "exit", "q"):
            break
        elif cmd in ("m", "map") and len(parts) >= 3:
            c, p = parts[1].upper(), parts[2].lower()
            if c not in ENGLISH_ALPHABET or p.upper() not in ENGLISH_ALPHABET:
                print(f"Error: Invalid letters '{parts[1]}' or '{parts[2]}'. Must be Latin A-Z.")
                continue
            state.map_letter(c, p)
            print(f"Mapped {c} -> {p}")
            preview = state.decode_text(ciphertext[:220])
            print(f"Preview: {preview}\n")
        elif cmd in ("swap", "sw") and len(parts) >= 3:
            p1, p2 = parts[1].lower(), parts[2].lower()
            ok, msg = state.swap_plain_letters(p1, p2)
            print(msg)
            if ok:
                preview = state.decode_text(ciphertext[:220])
                print(f"Preview: {preview}\n")
        elif cmd in ("u", "unmap") and len(parts) >= 2:
            c = parts[1].upper()
            state.unmap_letter(c)
            print(f"Unmapped {c}\n")
        elif cmd == "auto":
            print("Running automated solver...")
            auto = AutomatedSolver(ciphertext)
            best_key, score, _ = auto.solve(restarts=4, max_iterations=2500)
            state.load_mapping(best_key)
            print(f"Loaded automated solution (fitness score: {score:.2f}).")
            print_key_table(state)
            print("Decoded plaintext:\n")
            print(state.decode_clean_plaintext(ciphertext))
            print()
        elif cmd == "key":
            print_key_table(state)
        elif cmd == "text":
            print("\nCurrent decoded text (lowercase = decoded, uppercase = ciphertext):")
            print(state.decode_text(ciphertext))
            print()
        elif cmd == "solve":
            state.load_mapping(V2_GROUND_TRUTH_CIPHER_TO_PLAIN)
            print("Loaded ground truth key.")
            print_key_table(state)
            print("Decoded plaintext:\n")
            print(state.decode_clean_plaintext(ciphertext))
            print()
        elif cmd == "reset":
            state.reset()
            print("Reset all mappings.\n")
        else:
            print("Unknown command. Type 'm <C> <P>', 'swap <P1> <P2>', 'auto', 'key', 'text', 'solve', 'reset', or 'b'.")


def run_menu(initial_variant: int = 25) -> None:
    """Main interactive menu loop."""
    current_variant = initial_variant
    ciphertext, resolved_id, note = get_variant(current_variant)
    state = SubstitutionState()

    while True:
        ic = calculate_index_of_coincidence(ciphertext)
        letters_count = sum(1 for c in ciphertext if c.isalpha())

        print(f"\nMonoalphabetic Cryptanalysis Suite")
        print(f"Active variant: {current_variant} (Resolved: Variant {resolved_id})")
        print(f"Text metrics:   {letters_count} letters, Index of Coincidence = {ic:.5f}")
        print("1. Display ciphertext")
        print("2. Letter frequency analysis")
        print("3. N-gram analysis (bigrams and trigrams)")
        print("4. Interactive substitution sandbox")
        print("5. Run automated solver (hill-climbing)")
        print("0. Exit")

        try:
            choice = input("\nSelect an option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == "1":
            print(f"\nCiphertext (Variant {resolved_id}):")
            print(ciphertext)
            print()
        elif choice == "2":
            print_frequency_table(ciphertext)
        elif choice == "3":
            print_ngrams_table(ciphertext)
        elif choice == "4":
            run_interactive_sandbox(ciphertext, state)
        elif choice == "5":
            print("\nRunning automated hill-climbing solver...")
            auto = AutomatedSolver(ciphertext)
            best_key, score, _ = auto.solve(restarts=4, max_iterations=2500)
            state.load_mapping(best_key)
            print(f"Optimal score reached: {score:.2f}")
            print_key_table(state)
            print("Decoded plaintext:\n")
            print(state.decode_clean_plaintext(ciphertext))
            print()
        elif choice in ("0", "q", "exit"):
            break
        else:
            print("Invalid option. Please enter a number between 0 and 5.\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Monoalphabetic Cryptanalysis Suite (CS Laboratory 2)",
    )
    parser.add_argument(
        "--variant", "-v",
        type=int,
        default=25,
        help="variant number (default: 25, which resolves to Variant 2)",
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="path to external ciphertext file",
    )
    parser.add_argument(
        "--solve",
        action="store_true",
        help="execute complete cryptanalysis and print decrypted plaintext",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="display unigram frequencies and Index of Coincidence",
    )
    parser.add_argument(
        "--ngrams",
        action="store_true",
        help="display top bigrams, trigrams, and doubles",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="output clean decrypted plaintext only (for piping)",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="launch interactive cryptanalysis application",
    )

    args = parser.parse_args()

    # Load ciphertext from external file or assignment variant
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            ciphertext = f.read()
        resolved_id = 0
        variant_note = f"Custom file: {args.file}"
        active_variant = 0
    else:
        active_variant = args.variant
        ciphertext, resolved_id, variant_note = get_variant(active_variant)

    # Launch interactive mode if explicitly requested or run without flags
    if len(sys.argv) == 1 or args.interactive:
        run_menu(initial_variant=active_variant)
        return

    # Non-interactive CLI handlers
    if args.stats:
        ic = calculate_index_of_coincidence(ciphertext)
        print(f"{variant_note}")
        print(f"Index of Coincidence (IC): {ic:.5f} (English ref: {ENGLISH_IC:.4f}, Random ref: {RANDOM_IC:.4f})")
        print_frequency_table(ciphertext)

    if args.ngrams:
        print(f"{variant_note}")
        print_ngrams_table(ciphertext)

    if args.solve:
        state = SubstitutionState()
        if resolved_id == 2:
            state.load_mapping(V2_GROUND_TRUTH_CIPHER_TO_PLAIN)
        else:
            auto = AutomatedSolver(ciphertext)
            best_key, _, _ = auto.solve(restarts=5, max_iterations=3000)
            state.load_mapping(best_key)

        if args.clean:
            print(state.decode_clean_plaintext(ciphertext))
        else:
            print_key_table(state)
            print("Decrypted plaintext:\n")
            print(state.decode_clean_plaintext(ciphertext))


if __name__ == "__main__":
    main()
