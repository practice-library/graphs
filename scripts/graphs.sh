#!/usr/bin/env bash
# Prints every vendor graph directory, one per line, sorted: a directory <domain>/<vendor> whose
# check.json is one object naming "graph/nodes" as its instances. A check.json holding a list of
# targets (a contract's examples and counter-examples) is not a graph. The auto-merge allowlist and the CODEOWNERS
# lines without an owner are both generated from this list, one entry per graph.
# Usage: scripts/graphs.sh [root]
set -euo pipefail
root="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$root"
while IFS= read -r f; do
  instances="$(jq -r 'if type == "object" then .instances // empty else empty end' "$f")" || { echo "$f: not valid JSON" >&2; exit 1; }
  [ "$instances" = graph/nodes ] && dirname "$f"
done < <(find . -mindepth 3 -maxdepth 3 -type f -name check.json -not -path './selftest/*' | sed 's#^\./##' | LC_ALL=C sort)
exit 0
