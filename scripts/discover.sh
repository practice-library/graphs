#!/usr/bin/env bash
# Prints, as one JSON array, every schema check the gate runs, each {name, schema, instances, expect}:
#   every check.json:                       its schema on its instances, expect pass;
#   every contract (a directory with schema.json):
#     its examples/ directory,              expect pass;
#     each file in its counter-examples/,   on its own, expect fail.
# A contract without at least one example and one counter-example is an error.
# Paths are relative to the root. The selftest/ directory and .git are not searched.
# Usage: scripts/discover.sh [root]
set -euo pipefail
root="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$root"

found() { find . \( -path ./.git -o -path ./selftest \) -prune -o -type f -name "$1" -print | sed 's#^\./##' | LC_ALL=C sort; }

# Every step runs in this shell and checks its own status, so no error is lost in a subshell.
die() { echo "$*" >&2; exit 1; }
lines=""
add() { lines="$lines$1"$'\n'; }

while IFS= read -r f; do
  d="$(dirname "$f")"
  row="$(jq -c --arg d "$d" '
    def at($p): if $d == "." then $p else $d + "/" + $p end;
    if (type == "object") and ((keys | sort) == ["instances", "schema"])
    then {name: $d, schema: at(.schema), instances: at(.instances), expect: "pass"} else empty end' "$f")" \
    || die "$f: not valid JSON"
  [ -n "$row" ] || die "$f: keys must be exactly schema and instances"
  add "$row"
done < <(found check.json)

while IFS= read -r s; do
  d="$(dirname "$s")"
  for sub in examples counter-examples; do
    [ -n "$(find "$d/$sub" -type f -name '*.json' 2>/dev/null | head -1)" ] \
      || die "$d: a contract needs at least one $sub/*.json"
  done
  add "$(jq -nc --arg d "$d" --arg s "$s" '{name: ($d + " examples"), schema: $s, instances: ($d + "/examples"), expect: "pass"}')"
  while IFS= read -r c; do
    add "$(jq -nc --arg s "$s" --arg c "$c" '{name: $c, schema: $s, instances: $c, expect: "fail"}')"
  done < <(find "$d/counter-examples" -type f -name '*.json' | LC_ALL=C sort)
done < <(found schema.json)

targets="$(printf '%s' "$lines" | jq -sc '.')"
[ "$(jq 'length' <<<"$targets")" -gt 0 ] || { echo "nothing to check" >&2; exit 1; }
while IFS= read -r p; do
  [ -e "$p" ] || { echo "$p does not exist" >&2; exit 1; }
done < <(jq -r '.[] | .schema, .instances' <<<"$targets")
echo "$targets"
