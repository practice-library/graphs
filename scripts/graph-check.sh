#!/usr/bin/env bash
# Checks what a schema cannot see across files, for every vendor and regulation graph (scripts/graphs.sh):
#   each node file is named <id>.json, and its id names the graph: <type>.<vendor>.<slug> under vendors/<vendor>,
#   <type>.<jurisdiction>.<instrument>[.<part>] under regulations/<jurisdiction>-<topic>;
#   the graph has exactly one root node, vendor.<vendor> or jurisdiction.<jurisdiction>;
#   every edge points at a node of the same graph, so edges stay inside the graph;
#   every source's host is listed in policy/sources.json for this graph (its "vendor" is the directory name);
#   in a regulation graph, a status agrees with its window on measuredAt: in-force from the window on,
#   notified-not-in-force before it (draft and superseded are not compared with a date);
#   in a vendor graph, a node whose attrs.value is a number states that number in its quote (scripts/quote-value.py).
#   Regulation graphs are not checked for this yet (#69).
# Usage: scripts/graph-check.sh [root]
set -euo pipefail
root="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
vendor_graphs="$(bash "$here/graphs.sh" "$root" vendors)"
regulation_graphs="$(bash "$here/graphs.sh" "$root" regulations)"
cd "$root"

[ -n "$vendor_graphs$regulation_graphs" ] || { echo "no graph yet: nothing to check"; exit 0; }
[ -f policy/sources.json ] || { echo "FAIL policy/sources.json is missing"; exit 1; }

failed=0
check() { # <graph dir> <name the ids carry> <root id> <domain>
  local d="$1" v="$2" rootid="$3" dom="$4" key nodes records problems
  key="$(basename "$d")"
  nodes="$(find "$d/graph/nodes" -maxdepth 1 -type f -name '*.json' 2>/dev/null | LC_ALL=C sort)"
  if [ -z "$nodes" ]; then echo "FAIL $d: no node in graph/nodes"; failed=1; return; fi
  # One record per node: its file name and the node itself.
  records="$(while IFS= read -r f; do
      jq -c --arg file "$(basename "$f")" '{file: $file, node: .}' "$f" || echo '{"unreadable": true}'
    done <<<"$nodes" | jq -sc '.')"
  problems="$(jq -r --arg v "$v" --arg k "$key" --arg root "$rootid" --arg d "$d" --arg dom "$dom" --slurpfile s policy/sources.json '
    ([.[] | select(.unreadable) | "a node file is not valid JSON"]) +
    ( [.[] | select(.unreadable | not)] as $r
      | ($r | map(.node.id)) as $ids
      | ($s[0].hosts | map(select(.vendor == $k) | .host)) as $hosts
      | [ $r[]
          | .file as $file | .node as $n
          | (if $file != ($n.id + ".json") then "\($file): file name is not \($n.id).json" else empty end),
            (if ($n.id | split(".")[1]) != $v then "\($n.id): the id does not name \($v)" else empty end),
            ($n.edges[]? | select((.to as $t | $ids | index($t)) == null)
              | "\($n.id): edge \(.rel) points at \(.to), which is not a node of \($d)"),
            (($n.source | sub("^https://"; "") | split("/")[0]) as $h
              | if ($hosts | index($h)) == null then "\($n.id): source host \($h) is not listed for \($k) in policy/sources.json" else empty end),
            (select($dom == "regulations") | ($n.attrs.status? // null) as $st | ($n.attrs.window? // null) as $w
              | if $st == "in-force" and ($w == null or $w > $n.measuredAt) then "\($n.id): in-force but its window \($w) is after measuredAt \($n.measuredAt)"
                elif $st == "notified-not-in-force" and ($w == null or $w <= $n.measuredAt) then "\($n.id): notified-not-in-force but its window \($w) is not after measuredAt \($n.measuredAt)"
                else empty end)
        ]
      + (if ($ids | map(select(. == $root)) | length) != 1 then ["the graph needs exactly one root node, \($root)"] else [] end)
      + (if ($ids | length) != ($ids | unique | length) then ["two nodes share an id"] else [] end)
    ) | .[]' <<<"$records")"
  if [ -n "$problems" ]; then
    while IFS= read -r p; do echo "FAIL $d: $p"; done <<<"$problems"; failed=1
  else
    echo "ok   $d: $(jq 'length' <<<"$records") nodes, edges inside the graph, every source host listed"
  fi
}

while IFS= read -r d; do
  [ -z "$d" ] && continue # no vendor graph
  vendor="$(basename "$d")"
  check "$d" "$vendor" "vendor.$vendor" vendors
  if ! misses="$(python3 "$here/quote-value.py" "$d")"; then echo "$misses"; failed=1; fi
done <<<"$vendor_graphs"
while IFS= read -r d; do
  [ -n "$d" ] || continue
  name="$(basename "$d")"
  if ! [[ "$name" =~ ^[a-z]{2}-[a-z0-9]+(-[a-z0-9]+)*$ ]]; then echo "FAIL $d: a regulation graph is named <jurisdiction>-<topic>, such as in-data-governance"; failed=1; continue; fi
  jurisdiction="${name%%-*}"
  check "$d" "$jurisdiction" "jurisdiction.$jurisdiction" regulations
done <<<"$regulation_graphs"
exit "$failed"
