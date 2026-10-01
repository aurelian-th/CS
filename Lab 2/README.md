# Cryptography & Security — Laboratory Work 2
## Cryptanalysis of Monoalphabetic Substitution Ciphers

Author: Tihon Aurelian-Mihai  
Group: FAF-241  
Institution: Technical University of Moldova  
Supervisor: asis. univ. Zaica Maia  

---

### Description

Implementation of frequency analysis and cryptanalytic methods to break monoalphabetic substitution ciphers over the English alphabet ($n = 26$), adhering to the specifications of Laboratory Work 2.

The implementation is evaluated on the assigned student variant (**Variant 25**, resolved to **Variant 2** in accordance with the catalog modulo rule $((25 - 1) \bmod 23) + 1 = 2$). The intercepted ciphertext is an excerpt from David Kahn's *The Codebreakers* detailing early Egyptian cryptography and ancient secret writing.

### Methodological architecture

1. **Statistical unigram analysis:**
   - Computation of character counts and empirical frequencies across the 26-letter Latin alphabet.
   - Goodness-of-fit comparison against standard English linguistic distribution (Table 2.2 of the assignment).

2. **Index of Coincidence (IC):**
   - Computation of $IC = \frac{\sum f_i (f_i - 1)}{N (N - 1)}$.
   - Empirical validation: Variant 2 yields $IC = 0.06496$, matching natural English prose ($0.0667$) and distinguishing monoalphabetic ciphers from flat/polyalphabetic distributions ($0.0385$).

3. **N-gram & structural pattern deduction (Al-Kindi method):**
   - Identification of dominant trigram `WQV` (count 49) as `THE` ($W \to t, Q \to h, V \to e$).
   - Bigram resolution: `XG` (count 50) as `IN` ($X \to i, G \to n$), `WN` (count 32) as `TO` ($N \to o$).
   - Isolated single-letter token `t` (count 22) as indefinite article `A` ($T \to a$).
   - Conjunction and preposition deduction: `TGO` as `AND` ($O \to d$), `CNI` as `FOR` ($C \to f, I \to r$).
   - Domain-specific terminology: `hifuwnjituqf` as `cryptography`, `pvhivhf` as `secrecy`, `uinodhvo` as `produced`.
   - Comprehensive reconstruction of the 26-letter substitution alphabet.

4. **Stochastic automated solver:**
   - Hill-climbing algorithm with random restarts driven by English bigram log-probability scoring.

5. **Publication-grade visualization engine:**
   - Side-by-side frequency comparison bars, ranked decay curves, IC verification, and top bigram distributions.

### Directory structure

```
CS/Lab 2/
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── corpus.py          # English frequencies (Table 2.2), n-grams, scoring tables
│   ├── analyzer.py        # Frequency analysis, IC, Chi-square, n-grams
│   ├── variants.py        # 23 assignment variants & modulo resolution
│   ├── solver.py          # SubstitutionState, GuidedSolver, AutomatedSolver
│   ├── plots.py           # Publication-grade matplotlib charts
│   └── cli.py             # Minimalist interactive application & CLI
├── tests/
│   ├── __init__.py
│   └── test_crypto.py     # 19 comprehensive unit tests
├── figures/               # Generated 300 DPI analytical charts
│   ├── fig1_freq_comparison_v2.png
│   ├── fig2_freq_sorted_v2.png
│   ├── fig3_ic_metric_v2.png
│   └── fig4_bigrams_v2.png
├── CS_Lab2_Report.pdf     # Compiled academic laboratory report
├── Lucrare_de_laborator_nr_2_Criptanaliza_cifrurilor_monoalfabetice.pdf
└── README.md
```

### Usage

Interactive interface:
```bash
python3 src/cli.py
```
Or execute as module:
```bash
python3 -m src
```

Command-line flags:
```bash
# Display statistical frequency table and Index of Coincidence
python3 src/cli.py --variant 25 --stats

# Display top bigrams, trigrams, and doubled letters
python3 src/cli.py --variant 25 --ngrams

# Decrypt ciphertext and display substitution key table
python3 src/cli.py --variant 25 --solve

# Output clean plaintext only (suitable for piping)
python3 src/cli.py --variant 25 --solve --clean

# Analyze external ciphertext file
python3 src/cli.py --file path/to/ciphertext.txt --solve
```

### Testing

Run the test suite:
```bash
pytest -v
```
