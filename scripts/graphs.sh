#!/usr/bin/env bash
# Prints every graph directory of one domain, one per line, sorted: a directory <domain>/<name> whose
# check.json is one object naming "graph/nodes" as its instances. A check.json holding a list of
# targets (a contract's examples and counter-examples) is not a graph. The domain is vendors unless named:
# the auto-merge allowlist and the CODEOWNERS lines without an owner are both generated from the vendors
# list, one entry per graph, so a graph in any other domain (regulations) is never auto-merged.
# Usage: scripts/graphs.sh [root] [domain]
set -euo pipefail
root="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
domain="${2:-vendors}"
cd "$root"
[ -d "$domain" ] || exit 0
while IFS= read -r f; do
  instances="$(jq -r 'if type == "object" then .instances // empty else empty end' "$f")" || { echo "$f: not valid JSON" >&2; exit 1; }
  [ "$instances" = graph/nodes ] && dirname "$f"
done < <(find "$domain" -mindepth 2 -maxdepth 2 -type f -name check.json | LC_ALL=C sort)
exit 0
