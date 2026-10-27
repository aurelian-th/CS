# Oral Defense & Control Questions Guide — Laboratory Work 3
## Polyalphabetic Substitution Ciphers: Playfair & Vigenère

**Student:** Tihon Aurelian-Mihai  
**Group:** FAF-241  
**Supervisor:** asis. univ. Zaica Maia  
**Variant:** 25 (Odd variant $\implies$ Task 3.1 Playfair Cipher)

---

### Question 1: What is the fundamental distinction between monoalphabetic and polyalphabetic ciphers?

**Answer:**
In a monoalphabetic cipher (such as Caesar, affine, or general single-alphabet substitution), each character in the plaintext alphabet maps to exactly one fixed character in the ciphertext alphabet throughout the entire message. As a result, the unigram frequency distribution of the source natural language is directly preserved in the ciphertext, making it trivial to break using simple frequency analysis.

In contrast, a polyalphabetic cipher uses multiple substitution alphabets across consecutive character positions. A single plaintext character can map to multiple different ciphertext characters depending on its position and the current key symbol. Conversely, the same ciphertext letter can represent different plaintext letters. This flattens the frequency distribution, blending high-frequency letters with low-frequency letters and neutralizing naive single-letter frequency attacks.

---

### Question 2: How is the mathematical model of the Vigenère cipher formulated over the Romanian alphabet?

**Answer:**
The standard Romanian alphabet has $n = 31$ characters ($A, \breve{A}, \hat{A}, B, \dots, Ș, T, Ț, U, \dots, Z$), mapped to indices in $\mathbb{Z}_{31} = \{0, 1, \dots, 30\}$.

- **Key expansion:** A keyword $\mathcal{K} = (k_0, \dots, k_{d-1})$ of length $d \ge 7$ is repeated cyclically across the message of length $L$:
  $$\kappa_i = k_{i \bmod d}$$
- **Encryption formula:**
  $$c_i = (m_i + \kappa_i) \bmod 31$$
- **Decryption formula:**
  $$m_i = (c_i - \kappa_i) \bmod 31$$

Since 31 is a prime number, $\mathbb{Z}_{31}$ is a finite field $\mathbb{F}_{31}$, which ensures that every additive and subtractive operation is well-defined, unique, and has no degeneracies across sub-alphabets.

---

### Question 3: How is the Playfair cipher adapted to the Romanian language, and why is a $6 \times 5$ matrix used?

**Answer:**
The classical English Playfair cipher uses a $5 \times 5$ grid of 25 cells, merging `I` and `J` to fit the 26-letter English alphabet.

The Romanian alphabet consists of 31 letters. A $5 \times 5$ grid (25 cells) would require omitting 6 letters, which would severely distort Romanian spelling and diacritics. Instead:
- We merge the letter `J` into the cell of letter `I`. This choice is linguistically justified because `J` has the lowest natural frequency in Romanian and appears almost exclusively in foreign loanwords or specific proper names.
- This leaves exactly $31 - 1 = 30$ unique symbols.
- 30 factors naturally into $6 \times 5$ (6 rows and 5 columns) or $5 \times 6$, allowing all five Romanian diacritics ($\breve{A}, \hat{A}, \hat{I}, Ș, Ț$) to be preserved without loss.
- In decryption, any ambiguity between `I` and `J` is intuitively resolved from context by the reader.

---

### Question 4: What are the digraph preprocessing rules in the Playfair cipher, and why are they necessary?

**Answer:**
Before encrypting, the sanitized plaintext is divided into non-overlapping pairs (digraphs):
1. **Identical consecutive letters in a pair:** If a pair would consist of identical characters (e.g., `EE` in `FREEDOM`), a low-frequency filler letter (`X`, or alternatively `Z` if the duplicate is already `X`) is inserted between them (`EX ED OM`). This prevents a letter from occupying the same position in the matrix during transformation, which would lead to an undefined geometric configuration.
2. **Odd-length messages:** If after duplicate processing the total number of letters is odd, a terminal padding letter (`X` or `Z`) is appended so that every character belongs to a complete digraph pair.
3. **Punctuation and spacing:** Stripped during encryption; reconstructed manually after decryption according to linguistic logic.

---

### Question 5: What are the three geometric transformation rules in Playfair?

**Answer:**
Let $(r_1, c_1)$ and $(r_2, c_2)$ be the matrix coordinates of a digraph's letters on an $R \times C$ grid (with $R=6, C=5$):

1. **Same Row ($r_1 = r_2$):** Each letter shifts right by one column, wrapping cyclically modulo $C$:
   $$c_1' = (c_1 + 1) \bmod C, \quad c_2' = (c_2 + 1) \bmod C$$
   *(Decryption: subtract 1 modulo $C$, shifting left).*
2. **Same Column ($c_1 = c_2$):** Each letter shifts down by one row, wrapping cyclically modulo $R$:
   $$r_1' = (r_1 + 1) \bmod R, \quad r_2' = (r_2 + 1) \bmod R$$
   *(Decryption: subtract 1 modulo $R$, shifting up).*
3. **Rectangle ($r_1 \ne r_2$ and $c_1 \ne c_2$):** Each letter takes the column coordinate of the other letter on its own row:
   $$\text{Pair } 1 \to (r_1, c_2), \quad \text{Pair } 2 \to (r_2, c_1)$$
   *(Decryption: identically swap column coordinates, since swapping is self-inverse).*

---

### Question 6: What is the Index of Coincidence (IC), and how does it diagnose polyalphabetic ciphers?

**Answer:**
The Index of Coincidence (IC), introduced by William Friedman, is the probability that two randomly selected characters from a text are identical:
$$\text{IC} = \frac{\sum_{i=0}^{n-1} f_i (f_i - 1)}{N (N - 1)}$$

- For **natural Romanian text** ($n=31$), non-uniform letter distributions yield $\text{IC} \approx 0.0720$.
- For **pure uniform random noise**, $\text{IC}_{\text{random}} = \frac{1}{n} = \frac{1}{31} \approx 0.03226$.
- In a **monoalphabetic cipher**, the frequency distribution is preserved under permutation, so $\text{IC} \approx 0.0720$.
- In a **Vigenère cipher**, as key length $d$ grows, the ciphertext behaves like $d$ interleaved independent streams, and the expected IC decays according to:
  $$\text{IC}(d) = \frac{1}{d} \cdot \text{IC}_{\text{natural}} + \frac{d - 1}{d} \cdot \frac{1}{n}$$
  For $d = 7$, $\text{IC} \approx 0.0381$; for $d = 12$, $\text{IC} \approx 0.0349$.
  This metric allows a cryptanalyst to immediately differentiate monoalphabetic from polyalphabetic encryption, and estimate key length using the **Friedman test**.

---

### Question 7: How does Kasiski examination locate the key length of a Vigenère ciphertext?

**Answer:**
Kasiski examination exploits the fact that repeated sequences of plaintext letters that happen to be encrypted with the same segment of the repeating keyword will produce identical ciphertext sequences.
1. The cryptanalyst scans the ciphertext for repeated substrings of length 3, 4, or 5 (n-grams).
2. The distances between consecutive occurrences of identical n-grams are calculated.
3. The greatest common divisor (GCD) of these distance intervals reveals the most probable keyword length $d$ (or a multiple thereof).

---

### Question 8: How does Playfair's security compare to Vigenère, and how is Playfair cryptanalyzed?

**Answer:**
- **Playfair is a digraphic cipher:** Instead of substituting single characters ($n = 30$), it substitutes pairs of characters. There are $30 \times 29 = 870$ valid digraph pairs (since duplicate letters like `AA` are prevented). This significantly flattens single-letter frequencies.
- However, Playfair retains **digraph frequencies**: common Romanian digraphs (such as `DE`, `RE`, `IN`, `EA`, `TE`) will map to consistent ciphertext digraphs under the same key. A cryptanalyst can break Playfair by analyzing digraph frequencies and exploiting geometric matrix symmetries (e.g., if `AB` encrypts to `XY`, `BA` must encrypt to `YX` under rectangular rules).
- **Vigenère is a stream polyalphabetic cipher:** It shifts individual characters along cyclic alphabets. It is immune to digraph frequency attacks, but vulnerable to key-length determination (Kasiski/Friedman) followed by frequency analysis on the $d$ cosets.

---

### Question 9: Why was the minimum key length enforced at $|K| \ge 7$?

**Answer:**
For an alphabet of size $n = 31$:
- For a small key length such as $d = 3$, the total key space is only $31^3 = 29{,}791$ possible combinations, which can be exhaustively searched in milliseconds.
- For $d \ge 7$, the key space is at least $31^7 = 27{,}512{,}614{,}111 \approx 2.75 \times 10^{10}$ combinations.
- For $d = 12$, the key space reaches $31^{12} \approx 7.88 \times 10^{17}$ combinations.
Enforcing $|K| \ge 7$ ensures sufficient diffusion, prevents trivial periodic repetition, and raises brute-force complexity beyond manual inspection.

---

### Question 10: How does the software handle Romanian Unicode encoding ambiguities?

**Answer:**
Romanian diacritics exist in two historical Unicode encodings:
1. **Legacy ISO 8859-2 / Windows-1250 cedilla characters:** `Ş` (U+015E), `ş` (U+015F), `Ţ` (U+0162), `ţ` (U+0163).
2. **Official Unicode comma-below characters (Romanian standard):** `Ș` (U+0218), `ș` (U+0219), `Ț` (U+021A), `ț` (U+021B).

In `src/alphabet.py`, `CEDILLA_NORMALIZATION_MAP` intercepts and maps all cedilla variants to their corresponding standard comma-below representations before validating characters against the 31-letter Romanian set. If illegal characters (digits, symbols, punctuation) are entered, the program intercepts them, identifies the exact index position, and reports the allowed range to the user.
