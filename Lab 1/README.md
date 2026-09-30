# Cryptography & Security — Laboratory Work 1
## Caesar Cipher over the Romanian Alphabet

Author: Tihon Aurelian-Mihai  
Group: FAF-241  
Institution: Technical University of Moldova  
Supervisor: asis. univ. Zaica Maia  

---

### Description

Implementation of the Caesar cipher and the keyword-permuted Caesar cipher for the 31-letter Romanian alphabet ($n = 31$), adhering to the specifications of Laboratory Work 1.

The implementation strictly uses discrete mapping tables matching Table 2 of the assignment ($A = 0, \breve{A} = 1, \hat{A} = 2, \dots, Z = 30$) without relying on built-in character code points.

### Requirements implemented

1. **Task 1.1 — Caesar cipher (single key):**
   - Shift key $k \in \{1, \dots, 30\}$.
   - Modulo formulas: $c = (x + k) \bmod 31$ and $m = (y - k) \bmod 31$.
   - Normalization of cedilla letters ($\text{Ş}, \text{Ţ}, \text{ş}, \text{ţ} \to \text{Ș}, \text{Ț}$).
   - Removal of whitespace and conversion to uppercase.
   - Diagnostic validation identifying rejected characters and their positions.

2. **Task 1.2 — Caesar cipher with permutation (two keys):**
   - Shift key $k_1 \in \{1, \dots, 30\}$.
   - Keyword $k_2$ with minimum length of 7 Romanian letters.
   - Permuted alphabet construction: unique letters of $k_2$ followed by remaining Romanian letters in Table 2 order.
   - Formatted display of the permuted alphabet for verification.

### Directory structure

```
CS/Lab 1/
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── alphabet.py
│   ├── caesar.py
│   └── cli.py
├── tests/
│   └── test_caesar.py
├── CS_Lab1_Report.pdf
├── Laboratory Work no. 1. Caesar Cipher.pdf
└── README.md
```

### Usage

Interactive interface:
```bash
python3 src/cli.py
```

Command-line flags:
```bash
# Task 1.1 encryption
python3 src/cli.py --task 1.1 --mode encrypt --key 3 --text "cifrul cezar"

# Task 1.1 decryption
python3 src/cli.py --task 1.1 --mode decrypt --key 3 --text "FKITXOFHÂBT"

# Task 1.2 encryption
python3 src/cli.py --task 1.2 --mode encrypt --key 3 --keyword "criptografie" --text "cifrul cezar"

# Task 1.2 decryption
python3 src/cli.py --task 1.2 --mode decrypt --key 3 --keyword "criptografie" --text "POÂTXQPBIĂT"
```

### Testing

Run the test suite:
```bash
pytest -v
```
