#!/usr/bin/env bash
# Checks every contract in the repository. A contract is a directory holding schema.json, examples/
# and counter-examples/. For each one:
#   the schema is valid against its metaschema;
#   every file in examples/ is valid against the schema;
#   every file in counter-examples/, checked on its own, is invalid (a finding, exit 2), never an error.
# Usage: scripts/contracts.sh <path to the jsonschema binary>
set -euo pipefail
js="${1:?usage: scripts/contracts.sh <jsonschema binary>}"
finding=2
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

failed=0
contracts="$(git ls-files -- '*/schema.json' | while IFS= read -r f; do
  d="$(dirname "$f")"
  [ -d "$d/examples" ] && [ -d "$d/counter-examples" ] && echo "$d"
done)"
[ -n "$contracts" ] || { echo "no contract found" >&2; exit 1; }

while IFS= read -r d; do
  if "$js" metaschema "$d/schema.json" >/dev/null 2>&1; then echo "ok   $d/schema.json is a valid schema"
  else echo "FAIL $d/schema.json is not a valid schema"; failed=1; fi

  if "$js" validate "$d/schema.json" "$d/examples" >/dev/null 2>&1; then echo "ok   $d/examples are all valid"
  else echo "FAIL $d/examples: at least one is invalid"; "$js" validate "$d/schema.json" "$d/examples" || true; failed=1; fi

  n=0
  for c in "$d"/counter-examples/*.json; do
    n=$((n + 1))
    rc=0
    "$js" validate "$d/schema.json" "$c" >/dev/null 2>&1 || rc=$?
    if [ "$rc" -eq "$finding" ]; then echo "ok   $c is rejected"
    else echo "FAIL $c: expected a finding (exit $finding), got exit $rc"; failed=1; fi
  done
  [ "$n" -gt 0 ] || { echo "FAIL $d/counter-examples is empty"; failed=1; }
done <<<"$contracts"

exit "$failed"
