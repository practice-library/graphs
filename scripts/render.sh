#!/usr/bin/env bash
# Renders every file under templates/ to the same path at the repository root, replacing
# @@a.b.c@@ with that value from policy/constants.json (arrays and objects as compact JSON).
# @@gen.allowPaths@@ and @@gen.unowned@@ are generated from scripts/graphs.sh: one auto-merge
# allowlist entry and one CODEOWNERS line without an owner per vendor graph, the same list in both.
# @@gate.needs@@ is written both as the gate's needs and as .github/required-checks.json.
# A rendered .json file carries no header (JSON has no comments). A placeholder whose value is
# missing is an error.
# Usage: scripts/render.sh          write the rendered files
#        scripts/render.sh --check  write nothing; fail when a rendered file differs or is missing
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
mode="${1:-write}"
case "$mode" in write|--check) ;; *) echo "usage: scripts/render.sh [--check]" >&2; exit 2 ;; esac

constants="policy/constants.json"
graphs="$(bash scripts/graphs.sh)"
values="$(jq -c --arg graphs "$graphs" '
  ($graphs | split("\n") | map(select(length > 0))) as $g
  | . + {gen: {allowPaths: ($g | map(. + "/graph/nodes/")), unowned: ($g | map("/" + . + "/graph/nodes/") | join("\n"))}}' "$constants")"
failed=0
while IFS= read -r t; do
  out="${t#templates/}"
  rendered="$(jq -Rrs --argjson c "[$values]" --arg t "$t" '
    gsub("@@(?<k>[A-Za-z0-9_.]+)@@";
      (.k | split(".")) as $p
      | ($c[0] | getpath($p)) as $v
      | if $v == null then error($t + ": no value for @@" + .k + "@@ in policy/constants.json")
        elif ($v | type) == "string" then $v
        else ($v | tojson) end)' "$t")"
  # JSON has no comments, so a rendered .json file carries no header; it must still parse.
  if [ "${out##*.}" = json ]; then
    jq -e . >/dev/null <<<"$rendered" || { echo "FAIL $t does not render to valid JSON"; failed=1; continue; }
    content="$rendered"
  else
    content="# Generated from $t and $constants by scripts/render.sh. Do not edit."$'\n'"$rendered"
  fi
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
