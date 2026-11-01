"""A node's numeric value must be stated in its quote.

For every node file in each <graph dir>/graph/nodes/*.json whose attrs.value is a number (not a bool), the
quote must state that number. A quote states a number with:
  - digits, with optional , grouping and decimals (1,000  1,00,000  0.10), also with a unit glued on (500MB);
  - digits with a K, M or B multiplier suffix not followed by a letter (128K, 1M);
  - English or Indian number words (five thousand, two lakhs, twenty-five, two hundred and fifty).
When attrs.unit begins with a scale word (crore rupees, lakh ..., thousand ..., million ...), the value
times that scale also counts: value 250 with unit "crore rupees" is stated by "two hundred and fifty crore".
Prints FAIL <id>: value <v> is not stated in its quote for each miss and exits 1; prints nothing otherwise.
A node file that is not JSON is left to graph-check.sh, which reports it.
Python 3.9 or later, standard library only. Run: python3 scripts/quote-value.py <graph dir>...
"""
from __future__ import annotations

import glob
import json
import math
import os
import re
import sys

UNITS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen".split())}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SCALES = {"hundred": 100, "thousand": 1000, "lakh": 10**5, "lakhs": 10**5, "million": 10**6, "crore": 10**7,
          "crores": 10**7, "billion": 10**9}
SUFFIX = {"k": 1000, "m": 10**6, "b": 10**9}
# Digits not glued to a word or a decimal point before them; grouped (1,000 or 1,00,000) or plain, then an
# optional decimal part, then an optional K/M/B suffix that no letter follows (128K, 1M, but not 1MB).
DIGITS = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{2,3})+|\d+)(\.\d+)?(?:([kmb])(?![a-z]))?")


def numbers_in(text: str) -> set:
    """Every number the text states, as floats."""
    out = set()
    t = text.lower()
    for m in DIGITS.finditer(t):
        v = float(m.group(1).replace(",", "") + (m.group(2) or ""))
        out.add(v * SUFFIX[m.group(3)] if m.group(3) else v)
    cur = tot = 0
    seen = False
    for w in re.findall(r"[a-z]+|\S", t) + [""]:
        if w in UNITS or w in TENS:
            cur += UNITS.get(w, TENS.get(w, 0))
            seen = True
        elif w == "hundred" and seen:
            cur *= 100
        elif w in SCALES and seen:
            tot += max(cur, 1) * SCALES[w]
            cur = 0
        elif w in ("and", "-") and seen:
            continue
        else:  # the end of a number in words
            if seen:
                out.add(float(tot + cur))
            cur = tot = 0
            seen = False
    return out


def covers(quote: str, value, unit: str = "") -> bool:
    """The quote states value, or value times the scale word its unit begins with."""
    targets = [value]
    first = (unit or "").lower().split(" ")[0]
    if first in SCALES:
        targets.append(value * SCALES[first])
    return any(math.isclose(n, t, rel_tol=1e-9, abs_tol=1e-9) for n in numbers_in(quote) for t in targets)


def main(dirs: list) -> int:
    failed = 0
    for d in dirs:
        for path in sorted(glob.glob(os.path.join(d, "graph", "nodes", "*.json"))):
            try:
                with open(path, encoding="utf-8") as f:
                    node = json.load(f)
            except (OSError, ValueError):
                continue
            attrs = node.get("attrs") if isinstance(node, dict) else None
            if not isinstance(attrs, dict):
                continue
            value = attrs.get("value")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            quote = attrs.get("quote") if isinstance(attrs.get("quote"), str) else ""
            unit = attrs.get("unit") if isinstance(attrs.get("unit"), str) else ""
            if not covers(quote, value, unit):
                print(f"FAIL {node.get('id', path)}: value {json.dumps(value)} is not stated in its quote")
                failed = 1
    return failed


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
