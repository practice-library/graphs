#!/usr/bin/env bash
# Checks what a schema cannot see across files, for every vendor and regulation graph (scripts/graphs.sh):
#   each node file is named <id>.json, and its id names the graph: <type>.<vendor>.<slug> under vendors/<vendor>,
#   <type>.<jurisdiction>.<instrument>[.<part>] under regulations/<jurisdiction>-<topic>;
#   the graph has exactly one root node, vendor.<vendor> or jurisdiction.<jurisdiction>;
#   every edge points at a node of the same graph, so edges stay inside the graph;
#   every source's host is listed in policy/sources.json for this graph (its "vendor" is the directory name);
#   in a regulation graph, a status agrees with its window (a start date, or start/end, the end day inclusive)
#   on measuredAt: in-force from the start on and not past the end, notified-not-in-force before the start,
#   expired and repealed with an end before measuredAt, never-effective without an end (draft and superseded
#   are not compared with a date); a superseded or never-effective node has a node that supersedes it, and a
#   supersedes edge points at an ended node unless its source is still pending (policy/graph-rules.json);
#   in a vendor graph, a command, flag or argument is partOf a command or product (an argument: a command),
#   and a vendors/<vendor>/inventory.json is covered by command nodes (scripts/inventory-check.py);
#   language and practice graphs (languages/<name>, practices/<name>) are checked like vendor graphs:
#   ids <type>.<name>.<slug>, one root node language.<name> or practice.<name>;
#   a node whose attrs.value is a number states that number in its quote (scripts/quote-value.py; the
#   regulation nodes still to be re-quoted are listed in policy/graph-rules.json);
#   what the edges mean (scripts/graph-semantics.py, rules in policy/graph-rules.json, the checker's own
#   copy, not the root's): endpoint types per relation, no self-edge, no loop in an acyclic relation,
#   required provenance edges, a replaced node's status, and ids that continue their container's id.
# Usage: scripts/graph-check.sh [root]
set -euo pipefail
root="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
vendor_graphs="$(bash "$here/graphs.sh" "$root" vendors)"
regulation_graphs="$(bash "$here/graphs.sh" "$root" regulations)"
rules="$here/../policy/graph-rules.json"
language_graphs="$(bash "$here/graphs.sh" "$root" languages)"
practice_graphs="$(bash "$here/graphs.sh" "$root" practices)"
cd "$root"

[ -n "$vendor_graphs$regulation_graphs$language_graphs$practice_graphs" ] || { echo "no graph yet: nothing to check"; exit 0; }
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
  problems="$(jq -r --arg v "$v" --arg k "$key" --arg root "$rootid" --arg d "$d" --arg dom "$dom" --slurpfile s policy/sources.json --slurpfile rules "$rules" '
    def wstart: if . == null then null else split($rules[0].windows.intervalSeparator)[0] end;
    def wend: if . == null then null else (split($rules[0].windows.intervalSeparator) | if length > 1 then .[1] else null end) end;
    ([.[] | select(.unreadable) | "a node file is not valid JSON"]) +
    ( [.[] | select(.unreadable | not)] as $r
      | ($r | map(.node.id)) as $ids
      | ($r | map({key: .node.id, value: .node}) | from_entries) as $byid
      | ([$r[].node.edges[]? | select(.rel == "supersedes") | .to]) as $superseded
      | ($s[0].hosts | map(select(.vendor == $k) | .host)) as $hosts
      | [ $r[]
          | .file as $file | .node as $n
          | (if $file != ($n.id + ".json") then "\($file): file name is not \($n.id).json" else empty end),
            (if ($n.id | split(".")[1]) != $v then "\($n.id): the id does not name \($v)" else empty end),
            ($n.edges[]? | select((.to as $t | $ids | index($t)) == null)
              | "\($n.id): edge \(.rel) points at \(.to), which is not a node of \($d)"),
            (($n.source | sub("^https://"; "") | split("/")[0]) as $h
              | if ($hosts | index($h)) == null then "\($n.id): source host \($h) is not listed for \($k) in policy/sources.json" else empty end),
            (select($dom == "regulations") | ($n.attrs.status? // null) as $st | ($n.attrs.window? // null) as $w | ($w | wstart) as $ws | ($w | wend) as $we
              | if $we != null and $ws > $we then "\($n.id): its window \($w) ends before it starts"
                elif $st == $rules[0].status.inForce and ($w == null or $ws > $n.measuredAt) then "\($n.id): in-force but its window \($w) is after measuredAt \($n.measuredAt)"
                elif $st == $rules[0].status.inForce and $we != null and $we < $n.measuredAt then "\($n.id): in-force but its window \($w) ended before measuredAt \($n.measuredAt)"
                elif $st != null and ($rules[0].status.pending | index($st)) != null and ($w == null or $ws <= $n.measuredAt) then "\($n.id): \($st) but its window \($w) is not after measuredAt \($n.measuredAt)"
                elif $st != null and ($rules[0].status.ended | index($st)) != null and ($we == null or $we >= $n.measuredAt) then "\($n.id): \($st) but its window \($w) has no end before measuredAt \($n.measuredAt)"
                elif $st == $rules[0].status.neverEffective and $we != null then "\($n.id): \($st) never applied, so its window \($w) has no end"
                else empty end),
            (select($dom == "regulations") | ($n.attrs.status? // null) as $st
              | select($st != null and ($rules[0].status.needsReplacement | index($st)) != null and ($superseded | index($n.id)) == null)
              | "\($n.id): \($st) but no node supersedes it"),
            (select($dom == "regulations") | ($n.attrs.status? // null) as $st
              | $n.edges[]? | select(.rel == "supersedes") | ($byid[.to].attrs.status? // null) as $ts
              | select($st != null and $ts != null and ($rules[0].status.supersededTargets | index($ts)) == null and ($rules[0].status.mayReplaceInForce | index($st)) == null)
              | "\($n.id): \($st) supersedes \(.to), which is \($ts) and has not ended"),
            (select($dom == "vendors") | ($rules[0].cli.needsContainer[$n.type]? // null) as $need
              | select($need != null)
              | ([$n.edges[]? | select(.rel == $rules[0].cli.containmentRel) | $byid[.to].type?] | map(select(. as $t | $need | index($t))) | length) as $held
              | select($held == 0)
              | "\($n.id): a \($n.type) is \($rules[0].cli.containmentRel) a \($need | join(" or ")) of its graph")
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

semantic_and_quotes() { # <graph dir> <domain>: what the edges mean (policy/graph-rules.json), and a value in its quote
  local out
  if ! out="$(python3 "$here/graph-semantics.py" "$rules" "$2" "$1")"; then echo "$out"; failed=1; fi
  if ! out="$(python3 "$here/quote-value.py" --rules "$rules" "$2" "$1")"; then echo "$out"; failed=1; fi
}

while IFS= read -r d; do
  [ -z "$d" ] && continue # no vendor graph
  vendor="$(basename "$d")"
  check "$d" "$vendor" "vendor.$vendor" vendors
  semantic_and_quotes "$d" vendors
  if ! uncovered="$(python3 "$here/inventory-check.py" "$d")"; then echo "$uncovered"; failed=1; fi
done <<<"$vendor_graphs"
while IFS= read -r d; do
  [ -n "$d" ] || continue
  name="$(basename "$d")"
  if ! [[ "$name" =~ ^[a-z]{2}-[a-z0-9]+(-[a-z0-9]+)*$ ]]; then echo "FAIL $d: a regulation graph is named <jurisdiction>-<topic>, such as in-data-governance"; failed=1; continue; fi
  jurisdiction="${name%%-*}"
  check "$d" "$jurisdiction" "jurisdiction.$jurisdiction" regulations
  semantic_and_quotes "$d" regulations
done <<<"$regulation_graphs"
# Language and practice graphs: <domain>/<name>, ids <type>.<name>.<slug>, one root node of the domain's root type.
for domain in languages practices; do
  graphs="$language_graphs"; [ "$domain" = practices ] && graphs="$practice_graphs"
  root_type="$(jq -r --arg d "$domain" '.domains[$d].rootType' "$rules")"
  name_pattern="$(jq -r --arg d "$domain" '.domains[$d].graphName' "$rules")"
  while IFS= read -r d; do
    if [ -z "$d" ]; then continue; fi
    name="$(basename "$d")"
    if ! [[ "$name" =~ $name_pattern ]]; then echo "FAIL $d: a $domain graph is named in lower-case letters, digits and single hyphens"; failed=1; continue; fi
    check "$d" "$name" "$root_type.$name" "$domain"
  done <<<"$graphs"
done
exit "$failed"
