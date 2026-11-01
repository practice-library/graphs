"""Each guard in the scripts, mutated, must make a named self-test case fail.

GUARDS: for every row, copy scripts/ and selftest/ to a temporary directory, replace the guard's code with a
mutant that removes or inverts it (the code must occur exactly once, so a row cannot silently stop applying),
run scripts/selftest.sh there and require the named case to report FAIL. A mutant that leaves the case passing
means the guard is untested.

PINS: behaviour a mutant would only make stricter (or leave neutral for the gate), checked like GUARDS.

BACKSTOPS: early checks that only give a clearer message. Each is removed the same way, and the named case
must still fail, because the later check the row names catches the same input. A row whose case then passes
means the early check was carrying the failure alone and belongs in GUARDS.

Before any mutant, one unmutated run must pass every named case. Covered: graph-check.sh, graphs.sh,
quote-value.py and bump-only.sh. Not covered: render.sh (practice-library/graphs#25), the usage checks on argument counts, the
missing-directory exit in graphs.sh (without it, find reports the missing directory and lists nothing, the same output) and the measuredAt type test in bump-only.sh, which no input reaches alone.
Python 3.9 or later, standard library only. Run: python3 scripts/guards.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GC, BO, GR, QV = "scripts/graph-check.sh", "scripts/bump-only.sh", "scripts/graphs.sh", "scripts/quote-value.py"
C = "selftest/graph-check/"
F, K, P = "selftest/bump-only-file/", "selftest/bump-only-classify/", "selftest/bump-only-pr/"

GUARDS = [
    # (what the guard keeps true, file, code, mutant, the case that must then fail)
    ("a graph without nodes fails", GC,
     'then echo "FAIL $d: no node in graph/nodes"; failed=1; return; fi', "then return; fi", C + "empty-graph"),
    ("a node file that is not JSON fails", GC,
     'select(.unreadable) | "a node file is not valid JSON"', 'select(false) | "a node file is not valid JSON"',
     C + "node-not-json"),
    ("each file is named after its id", GC, 'if $file != ($n.id + ".json")', "if false", C + "file-name-not-id"),
    ("each id names its vendor", GC, 'if ($n.id | split(".")[1]) != $v', "if false", C + "id-names-other-vendor"),
    ("every edge points at a node of the same graph", GC,
     "select((.to as $t | $ids | index($t)) == null)", "select(false)", C + "edge-to-other-vendor"),
    ("every source host is listed", GC, "if ($hosts | index($h)) == null", "if false", C + "source-host-not-listed"),
    ("a host listed for another vendor does not count", GC,
     "map(select(.vendor == $k) | .host)", "map(.host)", C + "host-listed-for-other-vendor"),
    ("a host listed for another regulation graph does not count", GC,
     "map(select(.vendor == $k) | .host)", "map(select(.vendor | startswith($v)) | .host)", C + "regulation-host-listed-for-other-graph"),
    ("regulation graphs are checked", GC,
     'regulation_graphs="$(bash "$here/graphs.sh" "$root" regulations)"', 'regulation_graphs=""', C + "regulation-no-root"),
    ("a regulation graph's ids and root name its jurisdiction", GC,
     'jurisdiction="${name%%-*}"', 'jurisdiction="$name"', C + "regulation-complete"),
    ("a regulation graph is named <jurisdiction>-<topic>", GC,
     'if ! [[ "$name" =~ ^[a-z]{2}-[a-z0-9]+(-[a-z0-9]+)*$ ]]', "if false", C + "regulation-name-without-topic"),
    ("a regulation graph's name does not end in a hyphen", GC,
     "[a-z0-9]+(-[a-z0-9]+)*$ ]]", "[a-z0-9-]+$ ]]", C + "regulation-name-trailing-hyphen"),
    ("a jurisdiction is two letters", GC,
     "=~ ^[a-z]{2}-", "=~ ^[a-z]+-", C + "regulation-name-not-a-jurisdiction"),
    ("an empty vendor list checks no vendor graph", GC, '[ -z "$d" ] && continue # no vendor graph', "true",
     C + "regulation-complete"),
    ("an empty regulation list checks no regulation graph", GC, '[ -n "$d" ] || continue', "true", C + "complete"),
    ("status is compared with window only in regulation graphs", GC,
     'select($dom == "regulations")', "select(true)", C + "vendor-status-not-compared"),
    ("in-force needs its window on or before measuredAt", GC,
     'if $st == "in-force" and ($w == null or $w > $n.measuredAt)', "if false", C + "regulation-in-force-a-day-early"),
    ("in force from exactly the window date", GC, "or $w > $n.measuredAt)", "or $w >= $n.measuredAt)", C + "regulation-complete"),
    ("in-force without a window fails", GC, "($w == null or $w > $n.measuredAt)", "($w > $n.measuredAt)",
     C + "regulation-in-force-without-window"),
    ("notified-not-in-force needs its window after measuredAt", GC,
     'elif $st == "notified-not-in-force" and ($w == null or $w <= $n.measuredAt)', "elif false",
     C + "regulation-not-in-force-on-its-window"),
    ("not in force on the window date itself", GC, "or $w <= $n.measuredAt)", "or $w < $n.measuredAt)",
     C + "regulation-not-in-force-on-its-window"),
    ("a graph has exactly one root node", GC, '!= 1 then ["the graph needs', '> 1 then ["the graph needs',
     C + "no-root-node"),
    ("two node values may not share an id", GC,
     "if ($ids | length) != ($ids | unique | length) then", "if false then", C + "two-values-in-one-file"),
    ("a problem makes graph-check exit non-zero", GC, 'exit "$failed"', "exit 0", C + "edge-to-missing-node"),
    ("graph-check runs the quote-value check on each vendor graph", GC,
     'if ! misses="$(python3 "$here/quote-value.py" "$d")"; then', "if false; then", C + "value-not-in-quote"),
    ("a numeric value must be one of the numbers its quote states", QV,
     "if not covers(quote, value, unit):", "if False:", C + "value-not-in-quote"),
    ("only a check.json naming graph/nodes is a graph", GR,
     '[ "$instances" = graph/nodes ] && dirname "$f"', 'dirname "$f"', "selftest/graphs/two-graphs-and-a-contract"),
    ("graphs.sh lists vendors only, unless another domain is named", GR,
     'domain="${2:-vendors}"', 'domain="${2:-.}"', "selftest/graphs/regulations-not-in-default"),
    ("graphs.sh lists only inside the domain directory", GR,
     'find "$domain" -mindepth 2 -maxdepth 2', "find . -mindepth 3 -maxdepth 3", "selftest/graphs/regulations-not-in-default"),
    ("graphs.sh lists the domain it is given", GR,
     'domain="${2:-vendors}"', 'domain="vendors"', "selftest/graphs/regulations-when-named"),
    ("a path outside the allowlist goes to review", BO,
     'elif any($changes[]; allowed(.path) | not) then "review"', 'elif false then "review"', K + "outside-path"),
    ("an added or deleted node is rejected", BO,
     'elif all($changes[]; .status == "M") then "bump"', 'elif true then "bump"', K + "added-node"),
    ("a prefix entry covers only paths under it", BO,
     "then ($f | startswith($p))", 'then ($f | startswith($p | rtrimstr("/")))', K + "prefix-lookalike"),
    ("an exact entry covers only that path", BO,
     "else $f == $p end", "else ($f | startswith($p)) end", K + "exact-entry-lookalike"),
    ("an unreadable allowlist fails classify", BO,
     '"$diff")" || die "classify: unreadable input"', '"$diff")" || true',
     "selftest/bump-only-classify-fails/allow-not-json"),
    ("no field but measuredAt and attrs.fetched_at changes", BO,
     '|| die "a field other than measuredAt or attrs.fetched_at changed"', "|| true",
     F + "nested-measured-at-changed"),
    ("no line but the two date lines changes", BO, '[ -z "$bad" ] || die', "true || die", F + "reformatted"),
    ("measuredAt is the date of fetched_at", BO,
     '|| die "measuredAt is not the date of fetched_at"', "|| true", F + "measured-at-not-fetch-date"),
    ("fetched_at moves forward", BO,
     "$n[0].attrs.fetched_at > $o[0].attrs.fetched_at", "$n[0].attrs.fetched_at >= $o[0].attrs.fetched_at",
     F + "fetched-at-unchanged"),
    ("the allowlist is read from the base commit", BO,
     "git show HEAD^1:.github/automerge-paths.json", "git show HEAD:.github/automerge-paths.json",
     P + "head-shrinks-allowlist"),
    ("a rejected pull request fails", BO,
     'reject) die "touches only allowlisted', 'reject) echo "touches only allowlisted', P + "node-added-only"),
    ("every allowlisted change is a date bump", BO,
     'file_check "$tmp/old.json" "$tmp/new.json" >/dev/null ||', "true ||", P + "value-change-only-nodes"),
    ("every changed file is checked, not only the first", BO,
     'done < "$tmp/diff"', 'done < <(head -n1 "$tmp/diff")', P + "bump-then-value-change"),
    ("a nested fetched_at is not one of the two dates", BO,
     '($o[0] | del(.measuredAt, .attrs.fetched_at)) == ($n[0] | del(.measuredAt, .attrs.fetched_at))',
     '($o[0] | del(.measuredAt, (.. | .fetched_at?))) == ($n[0] | del(.measuredAt, (.. | .fetched_at?)))',
     F + "nested-fetched-at-changed"),
]

PINS = [
    # Behaviour a mutant would make stricter or leave neutral for the gate, pinned like a guard so it cannot
    # change unnoticed: (what is pinned, file, code, mutant, the case that must then fail)
    ("only a pull request is checked", BO,
     '[ "${GITHUB_EVENT_NAME:-}" = pull_request ] || {', "true || {", P + "not-a-pull-request"),
    ("a base commit without an allowlist allows nothing", BO,
     "echo '[]' > \"$tmp/allow\"", "echo '[\"vendors/\", \".github/\"]' > \"$tmp/allow\"", P + "no-base-allowlist"),
    ("a change of nothing goes to review", BO,
     'if ($changes | length) == 0 then "review"', 'if ($changes | length) == 0 then "bump"', K + "no-changes"),
]

BACKSTOPS = [
    # (what the early check keeps true, file, code, code without it, the case that must still fail, what catches it)
    ("a missing policy/sources.json fails", GC,
     '[ -f policy/sources.json ] || { echo "FAIL policy/sources.json is missing"; exit 1; }', "true",
     C + "no-sources-json", "jq --slurpfile on the missing file fails under set -e"),
    ("notified-not-in-force without a window fails", GC, "($w == null or $w <= $n.measuredAt)", "($w <= $n.measuredAt)",
     C + "regulation-not-in-force-without-window", "jq orders null before every string, so null <= measuredAt holds"),
    ("a check.json that is not JSON fails", GR,
     '|| { echo "$f: not valid JSON" >&2; exit 1; }', "", C + "check-json-not-json",
     "the jq call fails inside the command substitution under set -e"),
    ("the old file must be a JSON object", BO, '|| die "$old: not a JSON object"', "|| true",
     F + "old-not-object", "the field-equality jq call fails on a non-object"),
    ("the new file must be a JSON object", BO, '|| die "$new: not a JSON object"', "|| true",
     F + "new-not-object", "the field-equality jq call fails on a non-object"),
    ("an unreadable base allowlist fails", BO,
     """|| die "main's .github/automerge-paths.json is not valid JSON\"""", "|| true",
     P + "base-allowlist-not-json", "the paths-array check and classify reject the empty list"),
    ("a base allowlist without a paths array fails", BO,
     """|| die "main's .github/automerge-paths.json has no paths array\"""", "|| true",
     P + "base-allowlist-no-paths", "classify fails on a list that is not an array"),
]


def run(tmp: str) -> list:
    out = subprocess.run(["bash", "scripts/selftest.sh"], cwd=tmp, capture_output=True, text=True)
    return out.stdout.splitlines()


def copy(tmp: str) -> None:
    for d in ("scripts", "selftest"):
        shutil.copytree(os.path.join(ROOT, d), os.path.join(tmp, d))


def failed_case(lines: list, case: str) -> bool:
    return any(line.startswith(f"FAIL {case}:") for line in lines)


def passed_case(lines: list, case: str) -> bool:
    return any(line.startswith(f"ok   {case} ") for line in lines)


def mutated(path: str, code: str, mutant: str):
    """The self-test lines with code replaced by mutant, or why the replacement could not be made."""
    with tempfile.TemporaryDirectory() as tmp:
        copy(tmp)
        target = os.path.join(tmp, path)
        with open(target, encoding="utf-8") as f:
            text = f.read()
        if text.count(code) != 1:
            return f"the code occurs {text.count(code)} times in {path}, not once"
        with open(target, "w", encoding="utf-8") as f:
            f.write(text.replace(code, mutant))
        return run(tmp)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        copy(tmp)
        base = run(tmp)
    failed = [f"{row[0]}: its mutant is its code" for row in GUARDS + PINS + BACKSTOPS if row[2] == row[3]]
    failed += [f"{row[0]}: {row[4]} does not pass before any mutation"
              for row in GUARDS + PINS + BACKSTOPS if not passed_case(base, row[4])]
    if not failed:
        for what, path, code, mutant, case in GUARDS + PINS:
            lines = mutated(path, code, mutant)
            if isinstance(lines, str):
                failed.append(f"{what}: {lines}")
            elif failed_case(lines, case):
                print(f"ok   {what}: {case} fails without it")
            else:
                failed.append(f"{what}: {case} still passes with the guard mutated")
        for what, path, code, mutant, case, catcher in BACKSTOPS:
            lines = mutated(path, code, mutant)
            if isinstance(lines, str):
                failed.append(f"{what}: {lines}")
            elif passed_case(lines, case):
                print(f"ok   {what}: without it {case} still fails ({catcher})")
            else:
                failed.append(f"{what}: without it {case} passes, so it is a guard, not a backstop")
    for f in failed:
        print(f"FAIL {f}")
    print(f"{len(GUARDS)} guards, {len(PINS)} pins, {len(BACKSTOPS)} backstops, {len(failed)} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
