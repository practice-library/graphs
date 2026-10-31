#!/usr/bin/env bash
# Renders every file under templates/ to the same path at the repository root, replacing
# @@a.b.c@@ with that value from policy/constants.json (arrays and objects as compact JSON).
# @@gen.allowPathLines@@ and @@gen.unowned@@ are generated from scripts/graphs.sh: one auto-merge
# allowlist entry and one CODEOWNERS line without an owner per vendor graph, the same list in both.
# The allowlist writes each path on a line of its own and each separating comma on a line of its
# own, so adding a graph adds its own line (and one comma line) and changes no other entry's line.
# A graph whose path holds a denied term is left out of the allowlist (see below).
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

# A graph whose allowlist line would hold a term of .github/denylist.json is left out of the
# allowlist, so no change adds a denied line there; that graph's changes need a maintainer merge,
# as the denylist guard already fails on their content. Terms are formed as the guard forms them:
# the lower-case words of the line ([a-z0-9]+), each pair of adjacent words joined by one space,
# and each such pair written together; a term is denied when sha256(salt + ":" + term) is listed.
sha256() { if command -v sha256sum >/dev/null; then sha256sum; else shasum -a 256; fi | cut -d' ' -f1; }
denylist=".github/denylist.json"
allowed=""
while IFS= read -r g; do
  [ -n "$g" ] || continue
  if [ -f "$denylist" ]; then
    salt="$(jq -er '.salt | strings | select(length > 0)' "$denylist")" || { echo "FAIL $denylist has no salt" >&2; exit 1; }
    denied=0
    while IFS= read -r term; do
      if jq -e --arg h "$(printf '%s:%s' "$salt" "$term" | sha256)" '.sha256 | index($h) != null' "$denylist" >/dev/null; then denied=1; fi
    done < <(jq -rn --arg line "$(jq -n --arg p "$g/graph/nodes/" '$p')" '
      ($line | ascii_downcase | [scan("[a-z0-9]+")]) as $w
      | ($w + [range(0; ($w | length) - 1) | ($w[.] + " " + $w[. + 1]), ($w[.] + $w[. + 1])]) | unique[]')
    [ "$denied" = 0 ] || { echo "left out of the allowlist: $g (a denied term)" >&2; continue; }
  fi
  allowed+="$g"$'\n'
done <<<"$graphs"

values="$(jq -c --arg graphs "$graphs" --arg allowed "$allowed" '
  ($graphs | split("\n") | map(select(length > 0))) as $g
  | ($allowed | split("\n") | map(select(length > 0))) as $a
  | . + {gen: {allowPathLines: ("\n" + ($a | map((. + "/graph/nodes/" | tojson) + "\n") | join(",\n"))),
               unowned: ($g | map("/" + . + "/graph/nodes/") | join("\n"))}}' "$constants")"
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
