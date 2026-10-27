# Cryptography & Security — Laboratory Work 3
## Implementation of the Playfair cipher for Romanian language messages

Author: Tihon Aurelian-Mihai  
Group: FAF-241  
Institution: Technical University of Moldova  
Supervisor: asis. univ. Zaica Maia  

---

### Description

Implementation and verification of the Playfair polygraphic cipher adapted to the 31-letter Romanian alphabet ($n = 31$), adhering to the specifications of Laboratory Work 3.

In accordance with the student variant allocation, **Variant 25** (an odd catalog number) is assigned to **Task 3.1: Playfair cipher in Romanian**. The implementation supports bidirectional encryption and decryption, keyword validation, rectangular matrix geometry, and manual post-decryption space restoration.

### Methodological architecture

1. **Romanian alphabet adaptation ($n = 31$):**
   - The 31-letter Romanian character set ($A, \breve{A}, \hat{A}, B, \dots, Ș, T, Ț, U, \dots, Z$) is adapted to a 30-character key matrix by merging letter `J` into `I` due to the negligible natural frequency of `J` in Romanian.
   - The resulting 30 letters are arranged in a balanced $6 \times 5$ rectangular grid, fully preserving all 5 Romanian diacritical letters ($\breve{A}, \hat{A}, \hat{I}, Ș, Ț$).
   - Input sanitization strips whitespace and converts characters to uppercase.
   - Strict character domain validation: inputs outside the range `A`--`Z`, `a`--`z`, and Romanian diacritics are rejected with diagnostic error guidance.

2. **Digraph preparation and collision handling:**
   - Plaintext is segmented into consecutive two-letter blocks (digraphs).
   - If adjacent letters within a digraph are identical, an uncommon filler character (`X`, or alternately `Z`) is inserted between them.
   - If the cleaned text length is odd, a terminal padding character (`X` or `Z`) is appended to complete the final pair.

3. **Geometric transformation engine:**
   - **Same row:** Characters shift cyclically to the right ($\bmod 5$ columns). Decryption shifts left.
   - **Same column:** Characters shift cyclically downward ($\bmod 6$ rows). Decryption shifts upward.
   - **Rectangle:** Characters swap column coordinates within their respective rows. Decryption applies identical column coordinate exchange.

4. **Manual post-processing:**
   - The final phase of removing filler characters and inserting word boundaries is performed manually according to linguistic context and message logic.

### Directory structure

```
CS/Lab 3/
├── src/
│   ├── __init__.py
│   ├── __main__.py        # Entry point for module execution
│   ├── alphabet.py        # Romanian alphabet and character validation
│   ├── playfair.py        # PlayfairCipher engine (6x5 matrix, digraph rules, steps)
│   └── cli.py             # Dual-mode Unix CLI & interactive console interface
├── tests/
│   ├── __init__.py
│   └── test_ciphers.py    # Unit test suite covering alphabet, matrix, and cipher rules
├── CS_Lab3_Report.pdf     # Compiled academic laboratory report
├── Lucrare de laborator nr. 3. Cifruri polialfabetice.pdf
├── answers.md             # Oral defense questions & answers guide
└── README.md
```

### Usage

Interactive console menu:
```bash
python3 -m src -i
```

Command-line execution:
```bash
# Encrypt message with step-by-step transformation trace
python3 -m src --mode encrypt --key "CRIPTOGRAFIE" --text "SECURITATE" --steps

# Decrypt ciphertext
python3 -m src --mode decrypt --key "CRIPTOGRAFIE" --text "UGTQIPIEEH"

# Display Romanian alphabet numeric mapping
python3 -m src --show-alphabet
```

### Testing

Run the automated test suite for internal verification:
```bash
pytest -v
```
