"""Publication-grade visualization engine for frequency analysis and cryptanalysis metrics."""

import os
from typing import Dict, Optional, Tuple
import matplotlib
matplotlib.use("Agg")  # Headless backend
import matplotlib.pyplot as plt
import numpy as np

from .corpus import (
    ENGLISH_ALPHABET,
    ENGLISH_UNIGRAM_FREQS,
    ENGLISH_IC,
    RANDOM_IC,
    TOP_BIGRAMS,
)
from .analyzer import (
    calculate_relative_frequencies,
    calculate_index_of_coincidence,
    extract_ngrams,
)

# University publication style configuration
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["figure.dpi"] = 300

# Project directory paths
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_MODULE_DIR)
DEFAULT_FIGURES_DIR = os.path.join(_PROJECT_DIR, "figures")


def ensure_figures_dir(target_dir: str = DEFAULT_FIGURES_DIR) -> str:
    """Ensure output directory exists."""
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def plot_frequency_comparison(
    ciphertext: str,
    variant_id: int = 2,
    output_path: Optional[str] = None,
) -> str:
    """
    Generate side-by-side bar chart comparing standard English letter frequencies
    against intercepted ciphertext frequencies across the alphabet (A-Z).
    """
    if output_path is None:
        target_dir = ensure_figures_dir()
        output_path = os.path.join(target_dir, f"fig1_freq_comparison_v{variant_id}.png")

    cipher_freqs = calculate_relative_frequencies(ciphertext)
    letters = list(ENGLISH_ALPHABET)
    english_vals = [ENGLISH_UNIGRAM_FREQS[c] for c in letters]
    cipher_vals = [cipher_freqs[c] for c in letters]

    x = np.arange(len(letters))
    width = 0.38

    fig, ax = plt.subplots(figsize=(12, 5.2))

    rects1 = ax.bar(
        x - width / 2,
        english_vals,
        width,
        label="Standard English (Table 2.2)",
        color="#2b5c8f",
        edgecolor="#1a3a5c",
        linewidth=0.8,
        alpha=0.9,
    )
    rects2 = ax.bar(
        x + width / 2,
        cipher_vals,
        width,
        label=f"Ciphertext Variant {variant_id}",
        color="#c0392b",
        edgecolor="#78231a",
        linewidth=0.8,
        alpha=0.9,
    )

    ax.set_title(
        f"Letter Frequency Distribution: Standard English vs. Intercepted Ciphertext (Variant {variant_id})",
        pad=14,
        fontweight="bold",
    )
    ax.set_xlabel("Alphabet Letters (A – Z)", labelpad=8)
    ax.set_ylabel("Relative Frequency (%)", labelpad=8)
    ax.set_xticks(x)
    ax.set_xticklabels(letters, fontweight="medium")
    ax.set_ylim(0, max(max(english_vals), max(cipher_vals)) + 2.5)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cccccc", loc="upper right")

    # Annotate prominent peaks
    top_c = max(cipher_freqs.keys(), key=lambda c: cipher_freqs[c])
    idx_c = letters.index(top_c)
    ax.annotate(
        f"Peak: '{top_c}' ({cipher_freqs[top_c]:.1f}%)",
        xy=(idx_c + width / 2, cipher_freqs[top_c]),
        xytext=(idx_c - 1, cipher_freqs[top_c] + 1.2),
        arrowprops=dict(facecolor="#78231a", arrowstyle="->", lw=1.2),
        fontweight="bold",
        color="#78231a",
        fontsize=9,
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_frequency_sorted(
    ciphertext: str,
    variant_id: int = 2,
    output_path: Optional[str] = None,
) -> str:
    """
    Plot ranked frequency profiles comparing sorted ciphertext frequencies against
    sorted standard English frequencies, validating monoalphabetic substitution decay.
    """
    if output_path is None:
        target_dir = ensure_figures_dir()
        output_path = os.path.join(target_dir, f"fig2_freq_sorted_v{variant_id}.png")

    cipher_freqs = calculate_relative_frequencies(ciphertext)
    sorted_english = sorted(ENGLISH_UNIGRAM_FREQS.values(), reverse=True)
    sorted_cipher = sorted(cipher_freqs.values(), reverse=True)
    ranks = np.arange(1, 27)

    fig, ax = plt.subplots(figsize=(10, 4.8))

    ax.plot(
        ranks,
        sorted_english,
        marker="o",
        markersize=5,
        linewidth=2,
        color="#2b5c8f",
        label="Standard English (Descending Rank)",
    )
    ax.plot(
        ranks,
        sorted_cipher,
        marker="s",
        markersize=5,
        linewidth=2,
        linestyle="--",
        color="#c0392b",
        label=f"Ciphertext Variant {variant_id} (Descending Rank)",
    )

    ax.set_title(
        f"Ranked Frequency Decay Curves: English Baseline vs. Intercepted Ciphertext (Variant {variant_id})",
        pad=14,
        fontweight="bold",
    )
    ax.set_xlabel("Frequency Rank (1st to 26th Most Frequent Letter)", labelpad=8)
    ax.set_ylabel("Relative Frequency (%)", labelpad=8)
    ax.set_xticks(ranks)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cccccc", loc="upper right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_index_of_coincidence(
    ciphertext: str,
    variant_id: int = 2,
    output_path: Optional[str] = None,
) -> str:
    """
    Generate comparative bar chart of Index of Coincidence (IC), demonstrating
    that the intercepted text exhibits the monoalphabetic signature (IC ≈ 0.0667).
    """
    if output_path is None:
        target_dir = ensure_figures_dir()
        output_path = os.path.join(target_dir, f"fig3_ic_metric_v{variant_id}.png")

    observed_ic = calculate_index_of_coincidence(ciphertext)

    categories = [
        "Uniform Random\nDistribution (Flat)",
        f"Intercepted Ciphertext\n(Variant {variant_id})",
        "Natural English Prose\n(Linguistic Target)",
    ]
    values = [RANDOM_IC, observed_ic, ENGLISH_IC]
    colors = ["#7f8c8d", "#c0392b", "#27ae60"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(categories, values, width=0.48, color=colors, edgecolor="#2c3e50", linewidth=1.0)

    ax.set_title(
        f"Index of Coincidence (IC) Verification (Variant {variant_id})",
        pad=14,
        fontweight="bold",
    )
    ax.set_ylabel("Index of Coincidence", labelpad=8)
    ax.set_ylim(0, 0.082)
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    # Add numeric labels on top of bars
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            h + 0.002,
            f"{h:.5f}",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )

    # Draw horizontal threshold guide for English IC
    ax.axhline(ENGLISH_IC, color="#27ae60", linestyle=":", linewidth=1.5, alpha=0.7)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_top_bigrams(
    ciphertext: str,
    variant_id: int = 2,
    top_n: int = 10,
    output_path: Optional[str] = None,
) -> str:
    """Plot top N bigram occurrences in ciphertext."""
    if output_path is None:
        target_dir = ensure_figures_dir()
        output_path = os.path.join(target_dir, f"fig4_bigrams_v{variant_id}.png")

    bg_counts = extract_ngrams(ciphertext, n=2)[:top_n]
    if not bg_counts:
        return ""

    labels = [bg for bg, _ in bg_counts]
    values = [cnt for _, cnt in bg_counts]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.bar(labels, values, width=0.55, color="#2c3e50", edgecolor="#1a252f", linewidth=0.8)

    ax.set_title(
        f"Top {top_n} Ciphertext Bigrams (Variant {variant_id})",
        pad=14,
        fontweight="bold",
    )
    ax.set_xlabel("Bigram Token", labelpad=8)
    ax.set_ylabel("Occurrence Count", labelpad=8)
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            h + 0.8,
            str(h),
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def generate_all_plots(ciphertext: str, variant_id: int = 2) -> Dict[str, str]:
    """Generate and return filepaths for all publication figures."""
    p1 = plot_frequency_comparison(ciphertext, variant_id=variant_id)
    p2 = plot_frequency_sorted(ciphertext, variant_id=variant_id)
    p3 = plot_index_of_coincidence(ciphertext, variant_id=variant_id)
    p4 = plot_top_bigrams(ciphertext, variant_id=variant_id)
    return {
        "freq_comparison": p1,
        "freq_sorted": p2,
        "ic_metric": p3,
        "bigrams": p4,
    }
