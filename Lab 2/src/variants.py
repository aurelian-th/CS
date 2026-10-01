"""Variant retrieval and mapping management.

Provides access to the 23 laboratory assignment variants and implements
the university catalog modulo resolution rule.
"""

import json
import os
from typing import Dict, List, Tuple

# Base directory for laboratory data
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_MODULE_DIR), "data")
_VARIANTS_JSON_PATH = os.path.join(_DATA_DIR, "all_variants.json")

TOTAL_ASSIGNMENT_VARIANTS = 23


def _load_variants() -> Dict[int, str]:
    """Load all 23 assignment variants from JSON store."""
    if os.path.exists(_VARIANTS_JSON_PATH):
        with open(_VARIANTS_JSON_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return {int(k): v for k, v in raw.items()}
    raise FileNotFoundError(f"Variant database missing at {_VARIANTS_JSON_PATH}")


_CACHED_VARIANTS: Dict[int, str] = {}


def get_all_variants() -> Dict[int, str]:
    """Return dictionary of all available variants indexed by variant number."""
    global _CACHED_VARIANTS
    if not _CACHED_VARIANTS:
        _CACHED_VARIANTS = _load_variants()
    return _CACHED_VARIANTS


def resolve_variant_number(requested: int) -> Tuple[int, str]:
    """
    Apply university catalog modulo rule when requested variant exceeds total variants.

    Formula:
        resolved = ((requested - 1) % TOTAL_ASSIGNMENT_VARIANTS) + 1
    """
    if requested < 1:
        raise ValueError(f"Variant number must be positive (received {requested}).")

    if 1 <= requested <= TOTAL_ASSIGNMENT_VARIANTS:
        return requested, f"Direct catalog variant {requested}"

    resolved = ((requested - 1) % TOTAL_ASSIGNMENT_VARIANTS) + 1
    reason = (
        f"Variant {requested} resolved to Variant {resolved} via "
        f"(({requested} - 1) % {TOTAL_ASSIGNMENT_VARIANTS}) + 1"
    )
    return resolved, reason


def get_variant(variant_num: int = 25) -> Tuple[str, int, str]:
    """
    Retrieve ciphertext for specified variant.
    Defaults to student variant 25 (which maps to Variant 2).

    Returns:
        (ciphertext, resolved_variant_number, resolution_note)
    """
    resolved_num, note = resolve_variant_number(variant_num)
    all_vars = get_all_variants()
    if resolved_num not in all_vars:
        raise KeyError(f"Resolved variant {resolved_num} not found in database.")
    return all_vars[resolved_num], resolved_num, note


def list_available_variants() -> List[int]:
    """Return sorted list of available variant numbers."""
    all_vars = get_all_variants()
    return sorted(all_vars.keys())
