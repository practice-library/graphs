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
quote-value.py, graph-semantics.py, sources-check.py, report-check.py and bump-only.sh (not its check that a node is
unchanged between the report's commit and the base: the self-test builds only two commits). Not covered: index.sh
(scripts/index-selftest.sh runs its own cases), the policy lists graph-semantics.py skips by id (`exceptions`, `unless`), render.sh (practice-library/graphs#25), the usage checks on argument counts, the
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
GS, SC, S = "scripts/graph-semantics.py", "scripts/sources-check.py", "selftest/sources-check/"
RC, R = "scripts/report-check.py", "selftest/report-check/"
# Files outside scripts/ and selftest/ that the scripts read from their own checkout.
SUPPORT = ["policy/graph-rules.json", "policy/constants.json"]
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
     'if ! out="$(python3 "$here/quote-value.py" --rules "$rules" "$2" "$1")"; then', "if false; then",
     C + "value-not-in-quote"),
    ("graph-check runs the quote-value check on each regulation graph", GC,
     'if ! out="$(python3 "$here/quote-value.py" --rules "$rules" "$2" "$1")"; then', "if false; then",
     C + "regulation-value-not-in-quote"),
    ("graph-check runs the edge-meaning check on each vendor graph", GC,
     'semantic_and_quotes "$d" vendors', "true", C + "vendor-edge-wrong-endpoint-types"),
    ("graph-check runs the edge-meaning check on each regulation graph", GC,
     'semantic_and_quotes "$d" regulations', "true", C + "regulation-issued-by-timeline"),
    ("a failing edge-meaning check fails graph-check", GC,
     'if ! out="$(python3 "$here/graph-semantics.py" "$rules" "$2" "$1")"; then', "if false; then",
     C + "regulation-issued-by-timeline"),
    ("a graph-host key is listed once", SC, "if k in keys:", "if False:", S + "duplicate-host-key"),
    ("a robots url is the robots.txt of its own host", SC,
     'if r.hostname != h["host"] or r.path != "/robots.txt" or r.query:', "if False:", S + "robots-url-of-another-host"),
    ("a robots url is at the root of its host", SC, ' or r.path != "/robots.txt"', "",
     S + "robots-url-not-at-root"),
    ("every host entry has a scope", SC, "if k not in scope:", "if False:", S + "host-without-scope"),
    ("every scope has a host entry", SC, "if k not in keys:", "if False:", S + "scope-without-host"),
    ("a scope path is a directory path", SC, 'if not (p.startswith("/") and p.endswith("/")):', "if False:",
     S + "path-without-trailing-slash"),
    ("an unresolved permission gives its reason", SC, 'if not perm.get("reason"):', "if False:",
     S + "unresolved-without-reason"),
    ("an established permission gives its clause", SC,
     'if not perm.get("clause") or not perm.get("clauseUrl"):', "if False:", S + "established-without-clause"),
    ("a permission is established or unresolved", SC,
     "else:\n            out.append(f\"FAIL scope {s['vendor']} {s['host']}: permission.state",
     "elif False:\n            out.append(f\"FAIL scope {s['vendor']} {s['host']}: permission.state",
     S + "permission-state-unknown"),
    ("a blocked host is not approved", SC, "for h in sorted({k[1] for k in keys} & blocked):", "for h in []:",
     S + "blocked-host-listed"),
    ("a disallowed path is not cited", SC, 'if under(p, s.get("disallowed", [])):', "if False:",
     S + "disallowed-path-cited"),
    ("a cited path is inside the approved paths", SC, 'elif not under(p, s["paths"]):', "elif False:",
     S + "path-outside-scope"),
    ("a repository outside the approved ones is not cited", SC, 'elif not under(p, s["paths"]):', "elif False:",
     S + "other-repository-on-shared-host"),
    ("a bump needs its refresh report", BO, 'bound_to_report "$tmp" "$tmp/diff"', "true", P + "bump-without-report"),
    ("a report must be valid under the base's policy", BO,
     '|| die "$report: not valid under policy/sources.json"', "|| true", P + "report-breaks-the-byte-limit"),
    ("a report must support the bump", BO, '|| die "$path: the report does not support this bump"', "|| true",
     P + "report-fetched-at-differs"),
    ("a report must support the bump (outcome)", RC, 'if r["outcome"] != "unchanged":', "if False:",
     P + "report-outcome-changed"),
    ("a report must support the bump (fetch time)", RC, 'if r["fetchedAt"] != (new.get("attrs") or {}).get("fetched_at"):',
     "if False:", P + "report-fetched-at-differs"),
    ("a report names the commit it read", RC, 'if report.get("commit") != commit:', "if False:", R + "commit-differs"),
    ("requests is the number of fetches", RC, 'if report["requests"] != len(fetches):', "if False:",
     R + "requests-differs-from-fetches"),
    ("requests stays within the policy cap", RC, 'if report["requests"] > sources["maxRequestsPerRun"]:', "if False:",
     R + "requests-over-the-policy-cap"),
    ("robots.txt comes before any page", RC, "elif seen_page:", "elif False:", R + "robots-after-a-page"),
    ("a robots fetch is the host's /robots.txt", RC,
     'if f["kind"] == "robots" and urlsplit(f["url"]).path != "/robots.txt":', "if False:",
     R + "robots-fetch-not-at-root"),
    ("a request and its redirects stay on listed hosts", RC, "if host_of(hop) not in listed:", "if False:",
     R + "redirect-to-unlisted-host"),
    ("nothing is read from a host whose permission is unresolved", RC, "elif host_of(hop) in unresolved:",
     "elif False:", R + "host-permission-unresolved"),
    ("no response is longer than the host's maxBytes", RC, 'if entry and f["bytes"] > entry["maxBytes"]:', "if False:",
     R + "fetch-over-max-bytes"),
    ("no host gets more requests than its cap", RC, 'if h in listed and n > listed[h]["maxRequestsPerRun"]:',
     "if False:", R + "host-over-its-request-cap"),
    ("a robots record has its fetch", RC, "if h not in robots_fetched:", "if False:", R + "robots-record-without-fetch"),
    ("a page's host has a robots record that allows it", RC,
     'if r is None or r["verdict"] not in ("allowed", "absent"):', "if False:",
     R + "page-without-robots-record-for-its-host"),
    ("a refusal ends the run with an aborted record", RC, 'if "aborted" not in report:', "if False:",
     R + "refusal-without-abort"),
    ("a result's finalUrl is where its fetch ended", RC, 'if "finalUrl" in res and res["finalUrl"] != final:',
     "if False:", R + "final-url-not-where-the-fetch-ended"),
    ("a result's status is its fetch's", RC, 'if res.get("httpStatus") != f.get("httpStatus"):', "if False:",
     R + "result-status-differs-from-fetch"),
    ("a result lies inside the run", RC,
     'if not report["run"]["startedAt"] <= res["fetchedAt"] <= report["run"]["finishedAt"]:', "if False:",
     R + "result-fetched-outside-the-run"),
    ("a node may not have an edge to itself", GS, "if to == i:", "if False:", C + "vendor-edge-to-itself"),
    ("a relation joins only the type pairs it lists (vendor)", GS,
     'elif (n.get("type"), nodes[to].get("type")) not in rel_pairs.get(rel, set()):', "elif False:",
     C + "vendor-edge-wrong-endpoint-types"),
    ("a relation joins only the type pairs it lists (issuedBy)", GS,
     'elif (n.get("type"), nodes[to].get("type")) not in rel_pairs.get(rel, set()):', "elif False:",
     C + "regulation-issued-by-timeline"),
    ("a relation joins only the type pairs it lists (commencedBy)", GS,
     'elif (n.get("type"), nodes[to].get("type")) not in rel_pairs.get(rel, set()):', "elif False:",
     C + "regulation-commenced-by-instrument"),
    ("an acyclic relation has no loop", GS, 'for rel in rules.get("acyclic", []):', "for rel in []:",
     C + "regulation-supersedes-loop"),
    ("a required edge must be there", GS, 'if count < req.get("min", 0):', "if False:",
     C + "regulation-provision-without-part-of"),
    ("an instrument needs its issuer", GS, 'if count < req.get("min", 0):', "if False:",
     C + "regulation-instrument-without-issuer"),
    ("a duty needs its commencement", GS, 'if count < req.get("min", 0):', "if False:",
     C + "regulation-duty-without-commencement"),
    ("a required edge is not repeated past its maximum", GS, 'elif count > req.get("max", count):', "elif False:",
     C + "regulation-provision-part-of-twice"),
    ("a node a replacement edge names is superseded", GS,
     'if status is not None and status != sup["replaced"]:', "if False:",
     C + "regulation-replaced-node-still-in-force"),
    ("an id continues the id of the node it is part of", GS,
     'if tail(i)[:len(tail(e["to"]))] != tail(e["to"]) or len(tail(i)) <= len(tail(e["to"])):', "if False:",
     C + "regulation-id-does-not-continue-instrument"),
    ("a numeric value must be one of the numbers its quote states", QV,
     "and not covers(quote, value, unit):", "and False:", C + "value-not-in-quote"),
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
     'elif any($changes[]; .status == "M") and all($changes[]; .status == "M" or (.status == "A" and (.path | test($report)))) then "bump"',
     'elif true then "bump"', K + "added-node"),
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
    ("a report's graph is the graph the pull request touches", BO,
     '|| die "$report: its graph is not $graph"', "|| true", P + "report-of-another-graph",
     "report-check.py finds no listed host for the other vendor"),
    ("a report's commit is an ancestor of the base", BO,
     '|| die "$report: its commit $rc is not an ancestor of the base commit"', "|| true",
     P + "report-of-another-commit", "git diff fails on the commit that does not exist"),
    ("a report is added, never the only change", BO, 'any($changes[]; .status == "M") and ', "",
     P + "report-only", "bound_to_report finds no modified node"),
    ("only a report may be added beside a bump", BO, '(.status == "A" and (.path | test($report)))',
     '.status == "A"', P + "node-added-only", "no report is added, so bound_to_report fails"),
    ("a bump reads the node's source in the report", RC, 'if r["source"] != new.get("source"):', "if False:",
     P + "report-reads-another-source", "report-check.py check finds that source was not fetched"),
    ("a report has one result for the bumped node", RC, "if len(mine) != 1:", "if False:",
     P + "report-for-another-node", "indexing the empty list raises, and the input counts as unreadable"),
    ("every changed file is checked for its report, not only the first", BO, 'done < "$diff"',
     'done < <(head -n1 "$diff")', P + "bump-then-value-change",
     "the second loop's file check fails on the changed value"),
    ("a result's source was fetched", RC, "if f is None:", "if False:", R + "result-source-not-fetched",
     "subscripting None raises, and the input counts as unreadable"),
    ("a refusal stops every page fetch", RC, "if page_hosts:", "if False:", R + "page-fetched-after-a-refusal",
     "the page's host has no robots record that allows it"),
    ("a relation outside policy/graph-rules.json is named", GS, 'if rel not in rel_pairs:', "if False:",
     C + "vendor-relation-unknown", "an unlisted relation joins no pair, so the pair check rejects it"),
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
    for f in SUPPORT:
        os.makedirs(os.path.join(tmp, os.path.dirname(f)), exist_ok=True)
        shutil.copy(os.path.join(ROOT, f), os.path.join(tmp, f))


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
