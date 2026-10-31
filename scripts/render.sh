#!/usr/bin/env bash
# Renders every file under templates/ to the same path at the repository root, replacing
# @@a.b.c@@ with that value from policy/constants.json (arrays and objects as compact JSON).
# A placeholder whose value is missing is an error.
# Usage: scripts/render.sh          write the rendered files
#        scripts/render.sh --check  write nothing; fail when a rendered file differs or is missing
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
mode="${1:-write}"
case "$mode" in write|--check) ;; *) echo "usage: scripts/render.sh [--check]" >&2; exit 2 ;; esac

constants="policy/constants.json"
failed=0
while IFS= read -r t; do
  out="${t#templates/}"
  rendered="$(jq -Rrs --slurpfile c "$constants" --arg t "$t" '
    gsub("@@(?<k>[A-Za-z0-9_.]+)@@";
      (.k | split(".")) as $p
      | ($c[0] | getpath($p)) as $v
      | if $v == null then error($t + ": no value for @@" + .k + "@@ in policy/constants.json")
        elif ($v | type) == "string" then $v
        else ($v | tojson) end)' "$t")"
  header="# Generated from $t and $constants by scripts/render.sh. Do not edit."
  content="$header"$'\n'"$rendered"
  if [ "$mode" = --check ]; then
    if [ ! -f "$out" ] || [ "$(cat "$out")" != "$content" ]; then
      echo "FAIL $out differs from $t rendered; run scripts/render.sh"; failed=1
    else
      echo "ok   $out"
    fi
  else
    mkdir -p "$(dirname "$out")"
    printf '%s\n' "$content" > "$out"
    echo "wrote $out"
  fi
done < <(find templates -type f | LC_ALL=C sort)
exit "$failed"
