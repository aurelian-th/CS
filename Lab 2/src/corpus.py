"""English linguistic statistics and reference corpora.

Includes frequency tables, n-grams, and theoretical benchmarks
derived from the laboratory assignment specification (Table 2.2).
"""

from typing import Dict, List, Tuple
import math

ENGLISH_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Table 2.2 from laboratory specification: Letter frequencies in English (%)
ENGLISH_UNIGRAM_FREQS: Dict[str, float] = {
    "A": 8.17,
    "B": 1.49,
    "C": 2.78,
    "D": 4.25,
    "E": 12.70,
    "F": 2.23,
    "G": 2.01,
    "H": 6.09,
    "I": 6.97,
    "J": 0.15,
    "K": 0.77,
    "L": 4.03,
    "M": 2.41,
    "N": 6.75,
    "O": 7.51,
    "P": 1.93,
    "Q": 0.09,
    "R": 5.99,
    "S": 6.33,
    "T": 9.06,
    "U": 2.76,
    "V": 0.98,
    "W": 2.36,
    "X": 0.15,
    "Y": 1.97,
    "Z": 0.07,
}

# English letters sorted by descending frequency
ENGLISH_LETTERS_BY_FREQ: List[str] = sorted(
    ENGLISH_UNIGRAM_FREQS.keys(),
    key=lambda c: ENGLISH_UNIGRAM_FREQS[c],
    reverse=True,
)

# Prominent English bigrams as documented in laboratory assignment
TOP_BIGRAMS: List[str] = [
    "TH", "HE", "IN", "ER", "AN", "RE", "ED", "ON",
    "ES", "ST", "EN", "AT", "TO", "NT", "HA", "ND",
    "OU", "EA", "NG", "AS", "OR", "TI", "IS", "ET",
    "IT", "AR", "TE", "SE", "HI", "OF",
]

# Prominent English trigrams as documented in laboratory assignment
TOP_TRIGRAMS: List[str] = [
    "THE", "AND", "THA", "ENT", "ION", "TIO", "FOR",
    "NDE", "HAS", "NCE", "TIS", "OFT", "MEN",
]

# Prominent doubled letters in English
COMMON_DOUBLES: List[str] = ["SS", "EE", "TT", "FF", "LL", "MM", "OO"]

# Single-letter words in English
SINGLE_LETTER_WORDS: List[str] = ["A", "I"]

# Theoretical Index of Coincidence (IC)
ENGLISH_IC: float = 0.0667
RANDOM_IC: float = 1.0 / 26.0  # ~0.03846

# Common short English words for heuristic validation
COMMON_WORDS = {
    "THE", "OF", "AND", "TO", "A", "IN", "THAT", "IS", "WAS", "HE",
    "FOR", "IT", "WITH", "AS", "HIS", "ON", "BE", "AT", "BY", "I",
    "THIS", "HAD", "NOT", "ARE", "BUT", "FROM", "OR", "HAVE", "AN",
    "THEY", "WHICH", "ONE", "YOU", "WERE", "HER", "ALL", "SHE", "THERE",
    "WOULD", "THEIR", "WE", "HIM", "BEEN", "HAS", "WHEN", "WHO", "WILL",
    "MORE", "NO", "IF", "OUT", "SO", "SAID", "WHAT", "UP", "ITS",
    "ABOUT", "INTO", "THAN", "THEM", "CAN", "ONLY", "OTHER", "NEW", "SOME",
    "COULD", "TIME", "THESE", "TWO", "MAY", "THEN", "DO", "FIRST", "ANY",
    "MY", "NOW", "SUCH", "LIKE", "OUR", "OVER", "MAN", "ME", "EVEN",
    "MOST", "MADE", "AFTER", "ALSO", "DID", "MANY", "BEFORE", "MUST",
    "THROUGH", "BACK", "YEARS", "WHERE", "MUCH", "YOUR", "WAY", "WELL",
    "DOWN", "SHOULD", "BECAUSE", "EACH", "JUST", "THOSE", "PEOPLE", "MR",
    "HOW", "TOO", "LITTLE", "STATE", "GOOD", "VERY", "MAKE", "WORLD",
    "STILL", "OWN", "SEE", "MEN", "WORK", "LONG", "GET", "HERE", "BETWEEN",
    "BOTH", "LIFE", "BEING", "UNDER", "NEVER", "DAY", "SAME", "ANOTHER",
    "KNOW", "WHILE", "LAST", "MIGHT", "GREAT", "OLD", "YEAR", "OFF",
    "COME", "SINCE", "AGAINST", "GO", "CAME", "RIGHT", "USED", "TAKE",
    "THREE", "HIMSELF", "FEW", "HOUSE", "USE", "DURING", "WITHOUT", "AGAIN",
    "PLACE", "AMERICAN", "AROUND", "HOWEVER", "HOME", "SMALL", "FOUND",
    "MRS", "THOUGHT", "WENT", "SAY", "PART", "ONCE", "GENERAL", "HIGH",
    "UPON", "SCHOOL", "EVERY", "DON", "DOES", "GOT", "UNITED", "LEFT",
    "NUMBER", "COURSE", "WAR", "UNTIL", "ALWAYS", "AWAY", "SOMETHING",
    "FACT", "WATER", "THOUGH", "PUBLIC", "LESS", "PUT", "THINK", "ALMOST",
    "HAND", "ENOUGH", "FAR", "TOOK", "HEAD", "YET", "GOVERNMENT", "SYSTEM",
    "BETTER", "SET", "TOLD", "NOTHING", "NIGHT", "END", "WHY", "CALLED",
    "DIDN", "EYES", "FIND", "GOING", "LOOK", "ASKED", "LATER", "KNEW",
    "POINT", "NEXT", "PROGRAM", "CITY", "BUSINESS", "GIVE", "GROUP", "TOWARD",
    "DAYS", "ROOM", "PRESIDENT", "SIDE", "LOOKED", "CAR", "GIVEN", "SEVERAL",
    "TRUE", "GAME", "SHORT", "PUZZLE", "SCIENCE", "TODAY", "BEGINNING",
    "SECRET", "SECRECY", "CRYPTOGRAPHY", "CRYPTOLOGY", "CRYPTANALYSIS",
    "WRITING", "CODE", "CIPHER", "CIVILIZATION", "HISTORY",
}

# Standard English bigram log probabilities for fitness evaluation
STANDARD_BIGRAM_LOG_PROBS: Dict[str, float] = {}

# Approximate bigram relative frequencies based on standard English texts
_BIGRAM_RAW = {
    "TH": 3.56, "HE": 3.07, "IN": 2.43, "ER": 2.05, "AN": 1.99,
    "RE": 1.85, "ED": 1.76, "ON": 1.76, "ES": 1.45, "ST": 1.25,
    "EN": 1.13, "AT": 1.12, "TO": 1.07, "NT": 1.07, "HA": 0.93,
    "ND": 0.93, "OU": 0.87, "EA": 0.87, "NG": 0.86, "AS": 0.86,
    "OR": 0.84, "TI": 0.83, "IS": 0.82, "ET": 0.76, "IT": 0.74,
    "AR": 0.73, "TE": 0.73, "SE": 0.73, "HI": 0.72, "OF": 0.71,
    "CO": 0.69, "DE": 0.68, "LE": 0.67, "AL": 0.65, "RO": 0.64,
    "ME": 0.63, "RA": 0.61, "NE": 0.61, "LI": 0.60, "CH": 0.60,
    "LL": 0.58, "WA": 0.57, "LY": 0.55, "VE": 0.55, "MA": 0.54,
    "UR": 0.53, "LO": 0.52, "OM": 0.50, "RI": 0.50, "CE": 0.49,
    "LA": 0.48, "EE": 0.47, "SS": 0.45, "OO": 0.35, "TT": 0.35,
    "FF": 0.20, "MM": 0.18,
}

_FLOOR_PROB = 1e-5
for _bg, _pct in _BIGRAM_RAW.items():
    STANDARD_BIGRAM_LOG_PROBS[_bg] = math.log10(_pct / 100.0)


def get_bigram_log_prob(bg: str) -> float:
    """Return log10 probability for a bigram, with default floor penalty."""
    return STANDARD_BIGRAM_LOG_PROBS.get(bg.upper(), math.log10(_FLOOR_PROB))
