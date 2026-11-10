"""Dual-mode command-line and interactive console interface for DES key schedule."""

import argparse
import sys
from typing import Optional

from .des_key_schedule import (
    DESKeySchedule,
    apply_pc1,
    bin_to_hex,
    generate_random_64bit_key_hex,
    generate_random_k_plus,
    validate_and_parse_64bit_key,
    validate_and_parse_k_plus,
)


def prompt_round(default: int = 1) -> int:
    """Prompts user for round number between 1 and 16."""
    while True:
        try:
            raw = input(f"Enter round number (1-16, default {default}): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            sys.exit(0)

        if not raw:
            return default

        try:
            val = int(raw)
            if 1 <= val <= 16:
                return val
            print("Error: Round number must be between 1 and 16.")
        except ValueError:
            print("Error: Please enter a valid integer between 1 and 16.")


def prompt_k_plus() -> str:
    """Prompts user for 56-bit K+ in hexadecimal or binary format."""
    while True:
        try:
            raw = input("Enter K+ (14 hex digits or 56 binary bits): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            sys.exit(0)

        try:
            return validate_and_parse_k_plus(raw)
        except ValueError as exc:
            print(f"Error: {exc}")


def prompt_64bit_key() -> str:
    """Prompts user for 64-bit key in ASCII, hexadecimal, or binary format."""
    while True:
        try:
            raw = input("Enter 64-bit key (8 ASCII characters, 16 hex digits, or 64 bits): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            sys.exit(0)

        try:
            return validate_and_parse_64bit_key(raw)
        except ValueError as exc:
            print(f"Error: {exc}")


def display_single_round(
    schedule: DESKeySchedule,
    round_num: int,
    show_steps: bool = True,
    show_tables: bool = False,
    key_64_bin: Optional[str] = None,
) -> None:
    """Displays tables, intermediate state transformations, and the target round key Ki."""
    if show_tables:
        print()
        if key_64_bin:
            print(schedule.format_pc1_table())
            print()
        print(schedule.format_shift_schedule())
        print()
        print(schedule.format_pc2_table())
        print()

    if key_64_bin:
        key_hex = bin_to_hex(key_64_bin, 16)
        print(f"Original 64-bit key:")
        print(f"  Hexadecimal: {key_hex}")
        print(f"  Binary:      {key_64_bin}")
        print()

    c0_hex = bin_to_hex(schedule.c0, 7)
    d0_hex = bin_to_hex(schedule.d0, 7)
    k_plus_hex = bin_to_hex(schedule.k_plus, 14)

    print("Initial 56-bit key K+ (PC-1 output):")
    print(f"  Hexadecimal: {k_plus_hex}")
    print(f"  Binary:      {schedule.k_plus}")
    print(f"  Register C0: {schedule.c0} (hex: {c0_hex})")
    print(f"  Register D0: {schedule.d0} (hex: {d0_hex})")
    print()

    if show_steps:
        print(f"Intermediate round shift progression up to round {round_num}:")
        print("  Round | Shift | Register C (hex) | Register D (hex) | Concatenated CD (hex)")
        print("  ------+-------+------------------+------------------+----------------------")
        for r in range(1, round_num + 1):
            step = schedule.get_round(r)
            marker = " *" if r == round_num else "  "
            print(
                f"  {r:>5} | {step.shift:>5} | {step.c_hex:>16} | {step.d_hex:>16} | {step.cd_hex:>20}{marker}"
            )
        print()

    target_step = schedule.get_round(round_num)
    print(f"Target round {round_num} state:")
    print(f"  Left circular shift: {target_step.shift} bit(s)")
    print(f"  Register C{round_num}:        {target_step.c_curr} (hex: {target_step.c_hex})")
    print(f"  Register D{round_num}:        {target_step.d_curr} (hex: {target_step.d_hex})")
    print(f"  Combined (C{round_num} || D{round_num}): {target_step.cd_curr} (hex: {target_step.cd_hex})")
    print()

    print(f"Round key K{round_num} (PC-2 output, 48 bits):")
    print(f"  Hexadecimal: {target_step.key_hex}")
    print(f"  Binary:      {target_step.round_key}")
    print()
    print("  Partitioned into eight 6-bit S-box input blocks (B1 to B8):")
    blocks_formatted = "  ".join(
        f"B{idx + 1}: {block}" for idx, block in enumerate(target_step.key_blocks_6bit)
    )
    print(f"  {blocks_formatted}")


def display_schedule_summary(schedule: DESKeySchedule) -> None:
    """Displays complete 16-round schedule in tabular form."""
    header = (
        "  Round | Shift | Register C (hex) | Register D (hex) | "
        "Round key Ki (hex) | S-box blocks (B1..B4 | B5..B8)"
    )
    separator = (
        "  ------+-------+------------------+------------------+"
        "--------------------+---------------------------------"
    )
    print("Complete 16-round DES key schedule:")
    print(header)
    print(separator)
    for r in range(1, 17):
        step = schedule.get_round(r)
        b = step.key_blocks_6bit
        b_first = " ".join(b[:4])
        b_second = " ".join(b[4:])
        print(
            f"  {r:>5} | {step.shift:>5} | {step.c_hex:>16} | "
            f"{step.d_hex:>16} | {step.key_hex:>18} | {b_first} | {b_second}"
        )


def run_interactive() -> None:
    """Interactive console menu."""
    while True:
        print("\nDES key schedule (task 2.3: compute Ki from K+)")
        print("  1. Compute round key Ki from K+")
        print("  2. Compute round key Ki from 64-bit key")
        print("  3. Generate all 16 round keys")
        print("  4. Generate random K+ and compute Ki")
        print("  5. Show transformation tables")
        print("  0. Exit")

        try:
            choice = input("\nSelect option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            break

        if choice == "1":
            k_plus_bin = prompt_k_plus()
            round_num = prompt_round(default=3)
            schedule = DESKeySchedule(k_plus_bin)
            print()
            display_single_round(schedule, round_num=round_num, show_steps=True, show_tables=True)

        elif choice == "2":
            key_64_bin = prompt_64bit_key()
            round_num = prompt_round(default=3)
            k_plus_bin, _, _ = apply_pc1(key_64_bin)
            schedule = DESKeySchedule(k_plus_bin)
            print()
            display_single_round(
                schedule,
                round_num=round_num,
                show_steps=True,
                show_tables=True,
                key_64_bin=key_64_bin,
            )

        elif choice == "3":
            print("\nSource for key schedule:")
            print("  1. Enter K+ directly")
            print("  2. Enter 64-bit key")
            print("  3. Use random key")
            try:
                sub_choice = input("Select option (default 1): ").strip() or "1"
            except (KeyboardInterrupt, EOFError):
                print("\nExiting")
                break

            if sub_choice == "2":
                key_64_bin = prompt_64bit_key()
                k_plus_bin, _, _ = apply_pc1(key_64_bin)
            elif sub_choice == "3":
                k_plus_bin = generate_random_k_plus()
                print(f"Generated random K+ (hex): {bin_to_hex(k_plus_bin, 14)}")
            else:
                k_plus_bin = prompt_k_plus()

            schedule = DESKeySchedule(k_plus_bin)
            print()
            display_schedule_summary(schedule)

        elif choice == "4":
            k_plus_bin = generate_random_k_plus()
            print(f"Generated random K+ (hex): {bin_to_hex(k_plus_bin, 14)}")
            round_num = prompt_round(default=3)
            schedule = DESKeySchedule(k_plus_bin)
            print()
            display_single_round(schedule, round_num=round_num, show_steps=True, show_tables=True)

        elif choice == "5":
            print()
            print(DESKeySchedule.format_pc1_table())
            print()
            print(DESKeySchedule.format_shift_schedule())
            print()
            print(DESKeySchedule.format_pc2_table())

        elif choice == "0":
            print("Exiting")
            break
        else:
            print("Error: Unknown option, please select from the menu.")


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="DES key schedule generator and intermediate round analyzer (task 2.3)."
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="run in interactive console menu mode",
    )
    parser.add_argument(
        "--k-plus",
        type=str,
        help="56-bit key K+ as 14 hexadecimal characters or 56 binary bits",
    )
    parser.add_argument(
        "--key",
        type=str,
        help="64-bit key as 8 ASCII characters, 16 hexadecimal characters, or 64 binary bits",
    )
    parser.add_argument(
        "--round",
        type=int,
        default=3,
        help="target round index i between 1 and 16 (default: 3)",
    )
    parser.add_argument(
        "--all-rounds",
        action="store_true",
        help="display complete 16-round key schedule summary table",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="generate a cryptographically random K+ key",
    )
    parser.add_argument(
        "--show-tables",
        action="store_true",
        help="display PC-1, shift schedule, and PC-2 tables",
    )
    parser.add_argument(
        "--no-steps",
        action="store_true",
        help="suppress intermediate round progression table",
    )

    args = parser.parse_args()

    # Prioritize interactive menu as the default execution mode
    if args.interactive or not (args.k_plus or args.key or args.random or args.all_rounds or args.show_tables):
        run_interactive()
        return

    if args.show_tables and not (args.k_plus or args.key or args.random or args.all_rounds):
        print(DESKeySchedule.format_pc1_table())
        print()
        print(DESKeySchedule.format_shift_schedule())
        print()
        print(DESKeySchedule.format_pc2_table())
        return

    key_64_bin: Optional[str] = None
    k_plus_bin: Optional[str] = None

    if args.random:
        k_plus_bin = generate_random_k_plus()
        print(f"Generated random K+ (hex): {bin_to_hex(k_plus_bin, 14)}")
    elif args.k_plus:
        try:
            k_plus_bin = validate_and_parse_k_plus(args.k_plus)
        except ValueError as exc:
            print(f"Error: {exc}")
            sys.exit(1)
    elif args.key:
        try:
            key_64_bin = validate_and_parse_64bit_key(args.key)
            k_plus_bin, _, _ = apply_pc1(key_64_bin)
        except ValueError as exc:
            print(f"Error: {exc}")
            sys.exit(1)
    else:
        # Default fallback: NIST test vector
        default_hex = "133457799BBCDFF1"
        key_64_bin = validate_and_parse_64bit_key(default_hex)
        k_plus_bin, _, _ = apply_pc1(key_64_bin)
        print(f"Using standard NIST reference key: {default_hex}")

    schedule = DESKeySchedule(k_plus_bin)

    if args.all_rounds:
        display_schedule_summary(schedule)
    else:
        if not (1 <= args.round <= 16):
            print(f"Error: Round number must be between 1 and 16 (received {args.round}).")
            sys.exit(1)

        display_single_round(
            schedule,
            round_num=args.round,
            show_steps=not args.no_steps,
            show_tables=args.show_tables,
            key_64_bin=key_64_bin,
        )


if __name__ == "__main__":
    main()
