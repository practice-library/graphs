#!/usr/bin/env bash
# Prints, as one JSON array, every schema check the gate runs, each {name, schema, instances, expect}:
#   every check.json:                       its schema on its instances, expect pass;
#   every contract (a directory with schema.json):
#     its examples/ directory,              expect pass;
#     each file in its counter-examples/,   on its own, expect fail.
# Paths are relative to the root. The selftest/ directory and .git are not searched.
# Usage: scripts/discover.sh [root]
set -euo pipefail
root="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$root"

found() { find . \( -path ./.git -o -path ./selftest \) -prune -o -type f -name "$1" -print | sed 's#^\./##' | LC_ALL=C sort; }

targets="$({
  found check.json | while IFS= read -r f; do
    d="$(dirname "$f")"
    jq -c --arg d "$d" --arg f "$f" '
      def at($p): if $d == "." then $p else $d + "/" + $p end;
      if (type != "object") or ((keys | sort) != ["instances", "schema"]) then error($f + ": keys must be exactly schema and instances")
      else {name: $d, schema: at(.schema), instances: at(.instances), expect: "pass"} end' "$f"
  done

  found schema.json | while IFS= read -r s; do
    d="$(dirname "$s")"
    if [ -d "$d/examples" ]; then
      jq -nc --arg d "$d" --arg s "$s" '{name: ($d + " examples"), schema: $s, instances: ($d + "/examples"), expect: "pass"}'
    fi
    if [ -d "$d/counter-examples" ]; then
      find "$d/counter-examples" -type f -name '*.json' | LC_ALL=C sort | while IFS= read -r c; do
        jq -nc --arg s "$s" --arg c "$c" '{name: $c, schema: $s, instances: $c, expect: "fail"}'
      done
    fi
  done
} | jq -sc '.')"
[ "$(jq 'length' <<<"$targets")" -gt 0 ] || { echo "nothing to check" >&2; exit 1; }
while IFS= read -r p; do
  [ -e "$p" ] || { echo "$p does not exist" >&2; exit 1; }
done < <(jq -r '.[] | .schema, .instances' <<<"$targets")
echo "$targets"
