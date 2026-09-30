#!/usr/bin/env python3
"""Command-line interface for the Romanian Caesar cipher."""

import sys
import os
import argparse
from typing import List

# Ensure package root is in sys.path when executed directly
if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.alphabet import (
        ROMANIAN_ALPHABET,
        ALPHABET_SIZE,
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
else:
    from .alphabet import (
        ROMANIAN_ALPHABET,
        ALPHABET_SIZE,
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


def display_alphabet(alphabet: List[str] | tuple[str, ...]) -> None:
    """Prints the alphabet with its numeric indices."""
    cols = 8
    for i in range(0, len(alphabet), cols):
        chunk = alphabet[i : i + cols]
        row = "  ".join(f"[{i + j:2d}] {ch}" for j, ch in enumerate(chunk))
        print(f"  {row}")
    print()


def prompt_key(prompt_text: str = "Enter shift key (1-30): ") -> int:
    """Prompt loop for shift key validation."""
    while True:
        try:
            raw = input(prompt_text).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        is_valid, key, error = validate_key(raw)
        if is_valid:
            return key
        print(f"Error: {error}\n")


def prompt_keyword(prompt_text: str = "Enter keyword (at least 7 letters): ") -> str:
    """Prompt loop for keyword validation."""
    while True:
        try:
            raw = input(prompt_text).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        is_valid, keyword, error = validate_keyword(raw)
        if is_valid:
            return keyword
        print(f"Error: {error}\n")


def prompt_text(prompt_text: str = "Enter text: ") -> str:
    """Prompt loop for plaintext or ciphertext validation."""
    while True:
        try:
            raw = input(prompt_text).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        is_valid, cleaned, error = validate_and_clean_text(raw)
        if is_valid:
            return cleaned
        print(f"Error: {error}\n")


def prompt_operation() -> str:
    """Prompt loop for choosing operation."""
    while True:
        try:
            choice = input("Operation (e for encrypt, d for decrypt): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        if choice in ("e", "encrypt", "1"):
            return "encrypt"
        elif choice in ("d", "decrypt", "2"):
            return "decrypt"
        print("Invalid choice. Enter 'e' to encrypt or 'd' to decrypt.\n")


def run_task_1_1() -> None:
    """Interactive handler for Task 1.1."""
    print("\nCaesar cipher (single key)")
    op = prompt_operation()
    key = prompt_key()

    if op == "encrypt":
        text = prompt_text("Enter plaintext: ")
        result = encrypt_caesar(text, key)
        print(f"\nPlaintext:  {text}")
        print(f"Ciphertext: {result}\n")
    else:
        text = prompt_text("Enter ciphertext: ")
        result = decrypt_caesar(text, key)
        print(f"\nCiphertext: {text}")
        print(f"Plaintext:  {result}\n")


def run_task_1_2() -> None:
    """Interactive handler for Task 1.2."""
    print("\nCaesar cipher with permutation (two keys)")
    op = prompt_operation()
    k1 = prompt_key("Enter shift key k1 (1-30): ")
    k2 = prompt_keyword("Enter keyword k2 (at least 7 letters): ")

    permuted = build_permuted_alphabet(k2)
    print(f"\nPermuted alphabet: {''.join(permuted)}")
    display_alphabet(permuted)

    if op == "encrypt":
        text = prompt_text("Enter plaintext: ")
        result, _ = encrypt_caesar_permuted(text, k1, k2)
        print(f"Plaintext:  {text}")
        print(f"Ciphertext: {result}\n")
    else:
        text = prompt_text("Enter ciphertext: ")
        result, _ = decrypt_caesar_permuted(text, k1, k2)
        print(f"Ciphertext: {text}")
        print(f"Plaintext:  {result}\n")


def run_menu() -> None:
    """Main interactive menu loop."""
    print("Caesar cipher (Romanian alphabet)")
    while True:
        print("1. Caesar cipher (single key)")
        print("2. Caesar cipher with permutation (two keys)")
        print("3. Display Romanian alphabet")
        print("0. Exit")

        try:
            choice = input("\nSelect an option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == "1":
            run_task_1_1()
        elif choice == "2":
            run_task_1_2()
        elif choice == "3":
            print(f"\nRomanian alphabet (length {len(ROMANIAN_ALPHABET)}):")
            display_alphabet(ROMANIAN_ALPHABET)
        elif choice in ("0", "q", "exit"):
            break
        else:
            print("Invalid option. Please enter 0, 1, 2, or 3.\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Romanian Caesar cipher implementation",
    )
    parser.add_argument(
        "--task",
        choices=["1.1", "1.2"],
        help="task to execute (1.1 for single key, 1.2 for two keys)",
    )
    parser.add_argument(
        "--mode",
        choices=["encrypt", "decrypt"],
        help="operation mode",
    )
    parser.add_argument(
        "--key", "-k",
        type=int,
        help="shift key (1-30)",
    )
    parser.add_argument(
        "--keyword", "-w",
        type=str,
        help="permutation keyword (at least 7 Romanian letters)",
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="input text",
    )
    parser.add_argument(
        "--show-alphabet",
        action="store_true",
        help="display the Romanian alphabet and exit",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="launch interactive menu",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1 or args.interactive:
        run_menu()
        return

    if args.show_alphabet:
        print(f"Romanian alphabet (length {len(ROMANIAN_ALPHABET)}):")
        display_alphabet(ROMANIAN_ALPHABET)
        return

    if not args.task or not args.mode or args.key is None or not args.text:
        parser.error("Non-interactive mode requires --task, --mode, --key, and --text.")

    ok_k, valid_k, err_k = validate_key(args.key)
    if not ok_k:
        print(f"Error: {err_k}", file=sys.stderr)
        sys.exit(1)

    ok_t, clean_t, err_t = validate_and_clean_text(args.text)
    if not ok_t:
        print(f"Error: {err_t}", file=sys.stderr)
        sys.exit(1)

    if args.task == "1.1":
        if args.mode == "encrypt":
            print(encrypt_caesar(clean_t, valid_k))
        else:
            print(decrypt_caesar(clean_t, valid_k))
    elif args.task == "1.2":
        if not args.keyword:
            parser.error("Task 1.2 requires --keyword.")
        ok_w, valid_w, err_w = validate_keyword(args.keyword)
        if not ok_w:
            print(f"Error: {err_w}", file=sys.stderr)
            sys.exit(1)

        perm = build_permuted_alphabet(valid_w)
        print(f"Permuted alphabet: {''.join(perm)}")
        if args.mode == "encrypt":
            res, _ = encrypt_caesar_permuted(clean_t, valid_k, valid_w)
            print(f"Ciphertext: {res}")
        else:
            res, _ = decrypt_caesar_permuted(clean_t, valid_k, valid_w)
            print(f"Plaintext: {res}")


if __name__ == "__main__":
    main()
