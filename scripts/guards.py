"""Each guard in the scripts, mutated, must make a named self-test case fail.

For every row: copy scripts/ and selftest/ to a temporary directory, replace the guard's code with the mutant
(the code must occur exactly once, so a row cannot silently stop applying), run scripts/selftest.sh there and
require the named case to report FAIL. A mutant that leaves the case passing means the guard is untested.
Python 3.9 or later, standard library only. Run: python3 scripts/guards.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GC, BO, GR = "scripts/graph-check.sh", "scripts/bump-only.sh", "scripts/graphs.sh"
C = "selftest/graph-check/"
F, K, P = "selftest/bump-only-file/", "selftest/bump-only-classify/", "selftest/bump-only-pr/"

GUARDS = [
    # (what the guard keeps true, file, code, mutant, the case that must then fail)
    ("a missing policy/sources.json fails", GC,
     'echo "FAIL policy/sources.json is missing"; exit 1;', 'echo "FAIL policy/sources.json is missing"; exit 0;',
     C + "no-sources-json"),
    ("a graph without nodes fails", GC,
     'then echo "FAIL $d: no node in graph/nodes"; failed=1; continue; fi', "then continue; fi", C + "empty-graph"),
    ("a node file that is not JSON fails", GC,
     'select(.unreadable) | "a node file is not valid JSON"', 'select(false) | "a node file is not valid JSON"',
     C + "node-not-json"),
    ("each file is named after its id", GC, 'if $file != ($n.id + ".json")', "if false", C + "file-name-not-id"),
    ("each id names its vendor", GC, 'if ($n.id | split(".")[1]) != $v', "if false", C + "id-names-other-vendor"),
    ("every edge points at a node of the same graph", GC,
     "select((.to as $t | $ids | index($t)) == null)", "select(false)", C + "edge-to-other-vendor"),
    ("every source host is listed", GC, "if ($hosts | index($h)) == null", "if false", C + "source-host-not-listed"),
    ("a host listed for another vendor does not count", GC,
     "map(select(.vendor == $v) | .host)", "map(.host)", C + "host-listed-for-other-vendor"),
    ("a graph has exactly one root node", GC, '!= 1 then ["the graph needs', '> 1 then ["the graph needs',
     C + "no-root-node"),
    ("a problem makes graph-check exit non-zero", GC, 'exit "$failed"', "exit 0", C + "edge-to-missing-node"),
    ("a check.json that is not JSON fails", GR,
     'echo "$f: not valid JSON" >&2; exit 1;', 'echo "$f: not valid JSON" >&2; exit 0;', C + "check-json-not-json"),
    ("only a check.json naming graph/nodes is a graph", GR,
     '[ "$instances" = graph/nodes ] && dirname "$f"', 'dirname "$f"', "selftest/graphs/two-graphs-and-a-contract"),
    ("a change of nothing goes to review", BO,
     'if ($changes | length) == 0 then "review"', 'if ($changes | length) == 0 then "bump"', K + "no-changes"),
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
    ("the old file must be a JSON object", BO, '|| die "$old: not a JSON object"', "|| exit 0", F + "old-not-object"),
    ("the new file must be a JSON object", BO, '|| die "$new: not a JSON object"', "|| exit 0", F + "new-not-object"),
    ("no field but measuredAt and attrs.fetched_at changes", BO,
     '|| die "a field other than measuredAt or attrs.fetched_at changed"', "|| true",
     F + "nested-measured-at-changed"),
    ("no line but the two date lines changes", BO, '[ -z "$bad" ] || die', "true || die", F + "reformatted"),
    ("measuredAt is the date of fetched_at", BO,
     '|| die "measuredAt is not the date of fetched_at"', "|| true", F + "measured-at-not-fetch-date"),
    ("fetched_at moves forward", BO,
     "$n[0].attrs.fetched_at > $o[0].attrs.fetched_at", "$n[0].attrs.fetched_at >= $o[0].attrs.fetched_at",
     F + "fetched-at-unchanged"),
    ("only a pull request is checked", BO,
     '[ "${GITHUB_EVENT_NAME:-}" = pull_request ] || {', "true || {", P + "not-a-pull-request"),
    ("the allowlist is read from the base commit", BO,
     "git show HEAD^1:.github/automerge-paths.json", "git show HEAD:.github/automerge-paths.json",
     P + "allowlist-read-from-base"),
    ("an unreadable base allowlist fails", BO,
     """|| die "main's .github/automerge-paths.json is not valid JSON\"""", "|| exit 0", P + "base-allowlist-not-json"),
    ("a base allowlist without a paths array fails", BO,
     """|| die "main's .github/automerge-paths.json has no paths array\"""", "|| exit 0", P + "base-allowlist-no-paths"),
    ("a rejected pull request fails", BO, 'reject) die "touches only allowlisted', 'reject) exit 0; die "touches only allowlisted',
     P + "node-added-only"),
    ("every allowlisted change is a date bump", BO,
     'file_check "$tmp/old.json" "$tmp/new.json" >/dev/null ||', "true ||", P + "value-change-only-nodes"),
]


def main() -> int:
    failed = []
    for what, path, code, mutant, case in GUARDS:
        with tempfile.TemporaryDirectory() as tmp:
            for d in ("scripts", "selftest"):
                shutil.copytree(os.path.join(ROOT, d), os.path.join(tmp, d))
            target = os.path.join(tmp, path)
            with open(target, encoding="utf-8") as f:
                text = f.read()
            if text.count(code) != 1:
                failed.append(f"{what}: the guard's code occurs {text.count(code)} times in {path}, not once")
                continue
            with open(target, "w", encoding="utf-8") as f:
                f.write(text.replace(code, mutant))
            out = subprocess.run(["bash", "scripts/selftest.sh"], cwd=tmp, capture_output=True, text=True)
            if f"FAIL {case}" in out.stdout:
                print(f"ok   {what}: {case} fails without it")
            else:
                failed.append(f"{what}: {case} still passes with the guard mutated")
    for f in failed:
        print(f"FAIL {f}")
    print(f"{len(GUARDS)} guards, {len(failed)} untested")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
