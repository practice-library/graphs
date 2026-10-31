#!/usr/bin/env bash
# Checks what a schema cannot see across files, for every vendor graph (scripts/graphs.sh):
#   each node file is named <id>.json, and its id names this vendor (<type>.<vendor>.<slug>);
#   the graph has exactly one root node, vendor.<vendor>;
#   every edge points at a node of the same graph, so edges stay inside the vendor;
#   every source's host is listed in policy/sources.json for this vendor.
# Usage: scripts/graph-check.sh [root]
set -euo pipefail
root="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
graphs="$(bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/graphs.sh" "$root")"
cd "$root"

[ -n "$graphs" ] || { echo "no vendor graph yet: nothing to check"; exit 0; }
[ -f policy/sources.json ] || { echo "FAIL policy/sources.json is missing"; exit 1; }

failed=0
while IFS= read -r d; do
  vendor="$(basename "$d")"
  nodes="$(find "$d/graph/nodes" -maxdepth 1 -type f -name '*.json' 2>/dev/null | LC_ALL=C sort)"
  if [ -z "$nodes" ]; then echo "FAIL $d: no node in graph/nodes"; failed=1; continue; fi
  # One record per node: its file name and the node itself.
  records="$(while IFS= read -r f; do
      jq -c --arg file "$(basename "$f")" '{file: $file, node: .}' "$f" || echo '{"unreadable": true}'
    done <<<"$nodes" | jq -sc '.')"
  problems="$(jq -r --arg v "$vendor" --arg d "$d" --slurpfile s policy/sources.json '
    ([.[] | select(.unreadable) | "a node file is not valid JSON"]) +
    ( [.[] | select(.unreadable | not)] as $r
      | ($r | map(.node.id)) as $ids
      | ($s[0].hosts | map(select(.vendor == $v) | .host)) as $hosts
      | [ $r[]
          | .file as $file | .node as $n
          | (if $file != ($n.id + ".json") then "\($file): file name is not \($n.id).json" else empty end),
            (if ($n.id | split(".")[1]) != $v then "\($n.id): the id does not name vendor \($v)" else empty end),
            ($n.edges[]? | select((.to as $t | $ids | index($t)) == null)
              | "\($n.id): edge \(.rel) points at \(.to), which is not a node of \($d)"),
            (($n.source | sub("^https://"; "") | split("/")[0]) as $h
              | if ($hosts | index($h)) == null then "\($n.id): source host \($h) is not listed for \($v) in policy/sources.json" else empty end)
        ]
      + (if ($ids | map(select(. == "vendor." + $v)) | length) != 1 then ["the graph needs exactly one root node, vendor.\($v)"] else [] end)
    ) | .[]' <<<"$records")"
  if [ -n "$problems" ]; then
    while IFS= read -r p; do echo "FAIL $d: $p"; done <<<"$problems"; failed=1
  else
    echo "ok   $d: $(jq 'length' <<<"$records") nodes, edges inside the graph, every source host listed"
  fi
done <<<"$graphs"
exit "$failed"
