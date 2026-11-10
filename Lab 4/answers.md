# Oral Defense & Control Questions Guide — Laboratory Work 4
## Block Ciphers: Data Encryption Standard (DES)

**Student:** Tihon Aurelian-Mihai  
**Group:** FAF-241  
**Supervisor:** asis. univ. Zaica Maia  
**Variant:** 25 ($25 \bmod 11 = 3 \implies \mathbf{Task\ 2.3}$)

---

### Question 1: What is the fundamental architecture of the Data Encryption Standard (DES)?

**Answer:**
The Data Encryption Standard (DES) is a symmetric block cipher standardized by the National Bureau of Standards (NBS, now NIST) in 1977 as FIPS PUB 46. Its foundational architectural specifications are:
- **Block size:** 64 bits ($8$ bytes). Plaintext and ciphertext blocks are processed in 64-bit chunks.
- **Key length:** 64 bits total, consisting of 56 effective key bits and 8 parity verification bits (located at positions 8, 16, 24, 32, 40, 48, 56, and 64 to ensure odd parity in each byte).
- **Number of rounds:** 16 iterative Feistel rounds.
- **Structural framework:** Balanced Feistel network with initial permutation (IP) at the beginning and inverse initial permutation ($\text{IP}^{-1}$) at termination.
- **Round keys:** 16 subkeys ($K_1, \dots, K_{16}$), each having a length of 48 bits, generated dynamically by the key schedule.

---

### Question 2: What is a Feistel cipher network and what is its primary structural advantage?

**Answer:**
A Feistel cipher is a symmetric structure named after Horst Feistel. In each round $i$ ($1 \le i \le 16$), the 64-bit input state is split into two equal 32-bit halves, left ($L_{i-1}$) and right ($R_{i-1}$):
$$L_i = R_{i-1}$$
$$R_i = L_{i-1} \oplus f(R_{i-1}, K_i)$$

where $f$ is the round function and $\oplus$ denotes bitwise XOR.

The defining operational advantage of a Feistel network is **guaranteed reversibility regardless of whether the round function $f$ is invertible**. Because the inverse of XOR is XOR itself ($A \oplus B \oplus B = A$), decryption uses the exact same hardware or algorithmic logic as encryption, with the sole modification that the round subkeys are applied in reverse chronological sequence ($K_{16}, K_{15}, \dots, K_1$):
$$R_{i-1} = L_i$$
$$L_{i-1} = R_i \oplus f(L_i, K_i)$$

This eliminated the requirement to design and implement distinct encryption and decryption circuits in hardware.

---

### Question 3: How does the DES key schedule operate, and what is $K^+$ (Task 2.1, 2.2, 2.3)?

**Answer:**
The DES key schedule transforms the 64-bit input key $K$ into sixteen 48-bit round subkeys ($K_1, \dots, K_{16}$):

1. **Permuted Choice 1 (PC-1):**
   - The 64-bit key passes through PC-1, which discards the 8 parity bits (multiples of 8) and permutes the remaining 56 effective bits.
   - The resulting 56-bit permuted key is denoted as $K^+$.
   - $K^+$ is partitioned into two 28-bit shift registers: left half $C_0$ and right half $D_0$:
     $$K^+ = \text{PC-1}(K) = C_0 \,\|\, D_0$$

2. **Circular left shift schedule:**
   - In each round $i \in \{1, \dots, 16\}$, registers $C_{i-1}$ and $D_{i-1}$ are simultaneously shifted cyclically to the left by $s_i$ bit positions:
     $$C_i = \text{ROL}_{28}(C_{i-1}, s_i), \quad D_i = \text{ROL}_{28}(D_{i-1}, s_i)$$
   - The shift amounts $s_i$ are:
     - $s_i = 1$ bit in rounds $i \in \{1, 2, 9, 16\}$;
     - $s_i = 2$ bits in rounds $i \in \{3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15\}$.
   - The cumulative sum of shifts across all 16 rounds is:
     $$4 \times 1 + 12 \times 2 = 28 \text{ bits}$$
     Since each register has length 28, a total shift of 28 bits returns registers $C_{16} = C_0$ and $D_{16} = D_0$, completing a closed cycle.

3. **Permuted Choice 2 (PC-2):**
   - For round $i$, the 28-bit registers $C_i$ and $D_i$ are concatenated into a 56-bit string $(C_i \,\|\, D_i)$.
   - PC-2 selects and permutes 48 bits from this 56-bit string, discarding 8 specific bits (bits 9, 18, 22, 25 from $C_i$, and bits 35, 38, 43, 54 from $D_i$).
   - The resulting 48-bit vector forms round key $K_i$.

---

### Question 4: How does student Task 2.3 fit into the complete DES algorithm?

**Answer:**
Student Variant 25 corresponds to Task 2.3 ($25 \bmod 11 = 3$):
$$\text{Task 2.3: Given } K^+ \text{ in the DES algorithm, determine the round key } K_i \text{ for a given } i.$$

This task models the core round key synthesis pipeline:
1. Input $K^+$ is received as 56 bits (or 14 hex characters) and split into initial registers $C_0$ and $D_0$ ($28$ bits each).
2. The algorithm computes the cumulative left circular shifts for rounds $1, \dots, i$ according to the DES shift specification.
3. At round $i$, registers $C_i$ and $D_i$ are concatenated into 56 bits: $CD_i = C_i \,\|\, D_i$.
4. Permuted Choice 2 (PC-2) maps the 56 bits to 48 bits, producing round subkey $K_i$.
5. The 48-bit round key $K_i$ is partitioned into eight 6-bit vectors $(B_1, \dots, B_8)$, which represent the exact inputs that XOR with the expanded right half $E(R_{i-1})$ before entering substitution boxes $S_1, \dots, S_8$ in Feistel round $i$.

---

### Question 5: What are the components and operations inside the DES round function $f(R_{i-1}, K_i)$?

**Answer:**
The round function takes the 32-bit right half $R_{i-1}$ and the 48-bit round key $K_i$, producing a 32-bit output through four successive stages:

1. **Expansion Permutation ($E$):**
   - Expands 32-bit $R_{i-1}$ to 48 bits by duplicating 16 border bits and permuting them.
   - Provides diffusion by ensuring that adjacent S-boxes receive overlapping bits from adjacent 4-bit nibbles.

2. **Key mixing ($\oplus$):**
   - The 48-bit expanded right half is XORed with the 48-bit round subkey $K_i$:
     $$A = E(R_{i-1}) \oplus K_i$$
   - The resulting 48-bit vector is partitioned into eight consecutive 6-bit blocks: $B_1, B_2, B_3, B_4, B_5, B_6, B_7, B_8$.

3. **Substitution boxes ($S_1$ to $S_8$):**
   - Each 6-bit block $B_j = (b_1, b_2, b_3, b_4, b_5, b_6)$ enters non-linear substitution box $S_j$.
   - Bit 1 and bit 6 form a 2-bit row index $r \in \{0, 1, 2, 3\}$.
   - Bits 2, 3, 4, 5 form a 4-bit column index $c \in \{0, \dots, 15\}$.
   - The matrix entry $S_j[r, c]$ yields a 4-bit output.
   - Concatenating the outputs of all 8 S-boxes yields a 32-bit vector.

4. **Permutation ($P$):**
   - A fixed 32-bit permutation that scrambles the bits so that each S-box output bit affects multiple distinct S-boxes in the subsequent round, accelerating diffusion.

---

### Question 6: Why are the S-boxes considered the most critical component of DES?

**Answer:**
1. **Sole source of non-linearity:** All other DES operations (IP, $\text{IP}^{-1}$, $E$, $P$, XOR, circular shifts, PC-1, PC-2) are strictly linear over $\text{GF}(2)$. If S-boxes were omitted or linear, the entire 16-round cipher would collapse into a single affine transformation solvable via Gaussian elimination in polynomial time.
2. **Resistance to differential cryptanalysis:** The S-box design criteria (classified until revealed by Don Coppersmith in 1994) specifically minimized the maximum entry in the Difference Distribution Table (DDT), ensuring that output XOR differences have low probability given input XOR differences.
3. **Resistance to linear cryptanalysis:** The design minimizes linear correlation between input bit subsets and output bit subsets.

---

### Question 7: What are weak, semi-weak, and possibly weak keys in DES?

**Answer:**
- **Weak keys (4 keys):**
  Occur when $C_0$ and $D_0$ consist of all zeros or all ones after PC-1:
  - All 0s in $C_0$, all 0s in $D_0$: `0x0101010101010101`
  - All 1s in $C_0$, all 1s in $D_0$: `0xFEFEFEFEFEFEFEFE`
  - All 0s in $C_0$, all 1s in $D_0$: `0x1F1F1F1F0E0E0E0E`
  - All 1s in $C_0$, all 0s in $D_0$: `0xE0E0E0E0F1F1F1F1`
  Since circular shifts do not modify all-zero or all-one strings, all 16 round keys are identical:
  $$K_1 = K_2 = \dots = K_{16}$$
  As a consequence, applying DES twice with a weak key produces the original plaintext ($\text{DES}_K(\text{DES}_K(P)) = P$).

- **Semi-weak keys (6 pairs = 12 keys):**
  Occur when $C_0$ and $D_0$ contain alternating bit patterns ($0101\dots$ or $1010\dots$). The shift schedule produces only two distinct subkeys, each repeated 8 times. A semi-weak key pair $(K_A, K_B)$ satisfies:
  $$\text{DES}_{K_A}(\text{DES}_{K_B}(P)) = P$$

---

### Question 8: Why is single DES obsolete, and how did Triple-DES (3DES) address this?

**Answer:**
- **Effective 56-bit key space:**
  $2^{56} \approx 7.2 \times 10^{16}$ possible keys. This key space was completely broken by brute force:
  - In 1998, the EFF DES cracker ("Deep Crack") broke a DES key in 56 hours.
  - In 2006, COPACOBANA (FPGA cluster) cracked DES in under 7 days for less than \$10,000.
  - Today, customized FPGA/ASIC rigs can crack a 56-bit key in minutes.

- **Triple-DES (3DES / TDEA):**
  Uses three sequential DES operations in Encrypt-Decrypt-Encrypt (EDE) mode:
  $$C = \text{DES}_{K_3}(\text{DES}^{-1}_{K_2}(\text{DES}_{K_1}(P)))$$
  - **Backward compatibility:** Setting $K_1 = K_2 = K_3$ makes the inner decryption invert the first encryption, yielding standard single DES:
    $$\text{DES}_{K}(\text{DES}^{-1}_{K}(\text{DES}_{K}(P))) = \text{DES}_K(P)$$
  - **Key length:** 168 bits total (112 effective security bits against Meet-in-the-Middle attacks with two or three independent keys).
  - **Deprecation:** 3DES was officially retired by NIST due to its 64-bit block size vulnerability to Sweet32 collision attacks (birthday bound after $2^{32}$ blocks).

---

### Question 9: Why was Double DES rejected in favor of Triple DES?

**Answer:**
Double DES computes $C = \text{DES}_{K_2}(\text{DES}_{K_1}(P))$ using two 56-bit keys ($112$ bits total). While one would expect $2^{112}$ security, Double DES is vulnerable to the **Meet-in-the-Middle (MitM) attack**:
1. Given known plaintext-ciphertext pair $(P, C)$:
   - Compute and store $M_1 = \text{DES}_{K_1}(P)$ for all $2^{56}$ possible $K_1$ values in a hash table.
   - For all $2^{56}$ possible $K_2$ values, compute $M_2 = \text{DES}^{-1}_{K_2}(C)$ and check for collisions in the table.
2. A match identifies candidate key pair $(K_1, K_2)$, verified with a second pair $(P', C')$.
3. Time complexity is $2^{56} + 2^{56} = 2^{57}$ operations, and memory complexity is $2^{56} \times 8$ bytes. Thus Double DES provides only $2^{57}$ computational security rather than $2^{112}$.

---

### Question 10: How does the Advanced Encryption Standard (AES) compare to DES?

**Answer:**
| Characteristic | Data Encryption Standard (DES) | Advanced Encryption Standard (AES) |
| :--- | :--- | :--- |
| **Standardization** | 1977 (FIPS 46) | 2001 (FIPS 197, Rijndael) |
| **Structural design** | Balanced Feistel cipher | Substitution-Permutation Network (SPN) |
| **Block size** | 64 bits (vulnerable to Sweet32) | 128 bits |
| **Key lengths** | 56 effective bits | 128, 192, or 256 bits |
| **Number of rounds** | 16 | 10 (128-bit), 12 (192-bit), 14 (256-bit) |
| **Mathematical field** | Boolean logic, permutation matrices | Galois Field $\text{GF}(2^8)$ arithmetic |
| **S-box inversion** | Asymmetric lookup | Inversion in $\text{GF}(2^8)$ + affine mapping |
| **Hardware efficiency** | Optimized for 1970s discrete hardware | High throughput in both software and hardware (AES-NI) |
| **Cryptographic status** | Broken / Obsolete | Current global standard |
