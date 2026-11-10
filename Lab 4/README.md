# Cryptography & Security — Laboratory Work 4
## Implementation of DES round key generation (Task 2.3)

Author: Tihon Aurelian-Mihai  
Group: FAF-241  
Institution: Technical University of Moldova  
Supervisor: asis. univ. Zaica Maia  

---

### Description

Implementation, algorithmic verification, and step-by-step trace analysis of the Data Encryption Standard (DES) round key schedule in accordance with the specifications of Laboratory Work 4.

In accordance with the student catalog variant allocation, **Variant 25** ($25 \bmod 11 = 3$) is assigned to **Task 2.3**:
$$\text{Given } K^+ \text{ in the DES algorithm, determine the round key } K_i \text{ for a given } i.$$

The application supports direct input of $K^+$ in hexadecimal or binary format, automatic derivation from a standard 64-bit key (ASCII or hexadecimal) via Permuted Choice 1 (PC-1), cryptographically random key generation, and intermediate round state visualization including 28-bit circular shifts, 56-bit register concatenation, and 48-bit Permuted Choice 2 (PC-2) mapping.

### Methodological architecture

1. **Permuted Choice 1 (PC-1) and register initialization:**
   - The 64-bit original key has its 8 parity bits (multiples of 8) discarded.
   - The remaining 56 effective bits are permuted to form $K^+$, which is partitioned into two 28-bit shift registers:
     $$K^+ = \text{PC-1}(K) = C_0 \,\|\, D_0$$
   - When $K^+$ is supplied directly by the user, $C_0$ receives the first 28 bits and $D_0$ receives the second 28 bits.

2. **Circular left shift schedule:**
   - In each round $j \in \{1, \dots, i\}$, registers $C$ and $D$ are simultaneously shifted left cyclically by $s_j \in \{1, 2\}$ bits:
     $$C_j = \text{ROL}_{28}(C_{j-1}, s_j), \quad D_j = \text{ROL}_{28}(D_{j-1}, s_j)$$
   - Shifts equal 1 bit for rounds 1, 2, 9, 16; shifts equal 2 bits for all other rounds.
   - The total shift across 16 rounds equals 28 bits, restoring registers $C_{16} = C_0$ and $D_{16} = D_0$.

3. **Permuted Choice 2 (PC-2) key compression:**
   - At target round $i$, the 28-bit registers $C_i$ and $D_i$ are concatenated to form the 56-bit string $(C_i \,\|\, D_i)$.
   - PC-2 selects and permutes 48 bits, discarding 8 specific bits (4 from $C_i$ and 4 from $D_i$).
   - The resulting 48-bit round subkey $K_i$ is output in hexadecimal, 48-bit binary, and partitioned into eight 6-bit S-box input blocks ($B_1$ to $B_8$).

### Directory structure

```
CS/Lab 4/
├── src/
│   ├── __init__.py
│   ├── __main__.py             # Module execution entrypoint
│   ├── tables.py               # DES permutation matrices (PC-1, PC-2, shift schedule, IP, E, P)
│   ├── des_key_schedule.py     # Core key schedule logic and step-by-step analyzer
│   └── cli.py                  # Dual-mode Unix CLI & interactive console interface
├── tests/
│   ├── __init__.py
│   └── test_key_schedule.py    # Pytest suite validating against NIST FIPS 46-3 test vectors
├── Lucrare de laborator nr. 4. Cifruri bloc. Algortimul DES.pdf
├── answers.md                  # Comprehensive oral defense questions & answers guide
└── README.md
```

### Usage

Interactive console menu:
```bash
python3 -m src -i
```

Command-line execution:
```bash
# Compute round key K3 from 56-bit K+ (hexadecimal) with step trace
python3 -m src --k-plus F0CCAAF556678F --round 3

# Compute round key K3 from 64-bit key with permutation tables displayed
python3 -m src --key 133457799BBCDFF1 --round 3 --show-tables

# Display full 16-round key schedule summary table
python3 -m src --all-rounds --k-plus F0CCAAF556678F

# Generate random K+ and compute target round key Ki
python3 -m src --random --round 5

# Show DES permutation tables
python3 -m src --show-tables
```

### Testing

Run the automated test suite for internal verification:
```bash
pytest -v
```
