"""Command-line and interactive console interface for the Romanian Playfair cipher."""

import sys
import argparse
from typing import Tuple

from .alphabet import ROMANIAN_ALPHABET, clean_text, validate_key
from .playfair import PlayfairCipher


def prompt_key() -> str:
    """Prompts user for an encryption key with length >= 7."""
    while True:
        try:
            raw = input("Enter key (at least 7 letters): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            sys.exit(0)

        try:
            return validate_key(raw, min_len=7)
        except ValueError as exc:
            print(f"Error: {exc}")


def prompt_text(prompt_msg: str) -> str:
    """Prompts user for valid Romanian text."""
    while True:
        try:
            raw = input(prompt_msg).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            sys.exit(0)

        try:
            return clean_text(raw)
        except ValueError as exc:
            print(f"Error: {exc}")


def show_alphabet(alphabet: Tuple[str, ...]) -> None:
    """Prints alphabet letters with numeric indices."""
    cols = 8
    for i in range(0, len(alphabet), cols):
        chunk = alphabet[i : i + cols]
        row = "  ".join(f"[{i + j:2d}] {ch}" for j, ch in enumerate(chunk))
        print(f"  {row}")


def run_interactive() -> None:
    """Interactive console menu."""
    while True:
        print("\nPlayfair cipher (Romanian alphabet, 6x5 matrix)")
        print("  1. Encrypt text")
        print("  2. Decrypt text")
        print("  3. Show key matrix")
        print("  4. Show Romanian alphabet")
        print("  0. Exit")

        try:
            choice = input("\nSelect option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            break

        if choice == "1":
            key = prompt_key()
            text = prompt_text("Enter plaintext: ")
            cipher = PlayfairCipher(key=key)
            print("\nKey matrix:")
            print(cipher.format_matrix())
            print("\nTransformation steps:")
            steps = cipher.get_steps(text, mode="encrypt")
            for s in steps:
                print(f"  Pair {s['index']:>2}: {s['in_pair']} {s['in_pos']} -> [{s['rule']:<11}] -> {s['out_pos']} {s['out_pair']}")
            ciphertext = cipher.encrypt(text)
            print(f"\nCiphertext: {ciphertext}")
        elif choice == "2":
            key = prompt_key()
            text = prompt_text("Enter ciphertext: ")
            if len(text) % 2 != 0:
                print(f"Error: Ciphertext length must be even (received {len(text)}).")
                continue
            cipher = PlayfairCipher(key=key)
            print("\nKey matrix:")
            print(cipher.format_matrix())
            print("\nTransformation steps:")
            steps = cipher.get_steps(text, mode="decrypt")
            for s in steps:
                print(f"  Pair {s['index']:>2}: {s['in_pair']} {s['in_pos']} -> [{s['rule']:<11}] -> {s['out_pos']} {s['out_pair']}")
            plaintext = cipher.decrypt(text)
            print(f"\nDecrypted text: {plaintext}")
            print("Note: Restore spaces and remove filler characters manually based on context.")
        elif choice == "3":
            key = prompt_key()
            cipher = PlayfairCipher(key=key)
            print("\nKey matrix:")
            print(cipher.format_matrix())
        elif choice == "4":
            print("\nRomanian alphabet (31 letters):")
            show_alphabet(ROMANIAN_ALPHABET)
        elif choice == "0":
            break
        else:
            print("Invalid selection, please try again.")


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Playfair cipher implementation for Romanian messages (6x5 matrix)"
    )
    parser.add_argument(
        "--mode",
        choices=["encrypt", "decrypt"],
        help="Operation mode",
    )
    parser.add_argument(
        "--key", "-k",
        type=str,
        help="Encryption key (at least 7 letters)",
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Input plaintext or ciphertext",
    )
    parser.add_argument(
        "--steps",
        action="store_true",
        help="Display pair transformation steps",
    )
    parser.add_argument(
        "--show-alphabet",
        action="store_true",
        help="Display the Romanian alphabet and exit",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Launch interactive console menu",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1 or args.interactive:
        run_interactive()
        return

    if args.show_alphabet:
        print("Romanian alphabet (31 letters):")
        show_alphabet(ROMANIAN_ALPHABET)
        return

    if not args.mode or not args.key or not args.text:
        parser.error("CLI execution requires --mode, --key, and --text.")

    try:
        cipher = PlayfairCipher(key=args.key)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        clean_t = clean_text(args.text)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.mode == "encrypt":
        if args.steps:
            print("Key matrix:")
            print(cipher.format_matrix())
            print("\nTransformation steps:")
            steps = cipher.get_steps(clean_t, mode="encrypt")
            for s in steps:
                print(f"  Pair {s['index']:>2}: {s['in_pair']} {s['in_pos']} -> [{s['rule']:<11}] -> {s['out_pos']} {s['out_pair']}")
            print()
        print(cipher.encrypt(clean_t))
    else:
        if len(clean_t) % 2 != 0:
            print(f"Error: Ciphertext length must be even (received {len(clean_t)}).", file=sys.stderr)
            sys.exit(1)
        if args.steps:
            print("Key matrix:")
            print(cipher.format_matrix())
            print("\nTransformation steps:")
            steps = cipher.get_steps(clean_t, mode="decrypt")
            for s in steps:
                print(f"  Pair {s['index']:>2}: {s['in_pair']} {s['in_pos']} -> [{s['rule']:<11}] -> {s['out_pos']} {s['out_pair']}")
            print()
        print(cipher.decrypt(clean_t))


if __name__ == "__main__":
    main()
