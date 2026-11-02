"""A vendor graph's command nodes must cover the versioned inventory of its CLI.

For each <graph dir> that holds an inventory file (the name is policy/graph-rules.json's inventory.file):

    {"tool": "<tool>", "release": "<version>", "salt": "<text>",
     "commands": ["worktree rm", {"sha256": "<hex>"}],
     "notCovered": [{"path": "completion", "reason": "..."}, {"sha256": "<hex>", "reason": "..."}]}

  - release equals the attrs.scope of a release node of the graph, so the inventory names the pinned release;
  - commands lists every command path of that release, taken from the upstream definitions: words separated by
    one space, such as "worktree rm". An entry whose words include a denylisted word is stored as
    {"sha256": "<hex>"}, the digest of salt + ":" + the path (the hash name, here sha256, is inventory.hash in
    the policy file);
  - a command node is command.<vendor>.<tool>.<word>.<word>...; its path is the words after the tool;
  - every path listed has a command node or a notCovered entry with a reason, not both;
  - every command node and every notCovered entry is a listed path, so nothing is invented and nothing is stale;
  - no path is listed twice.
Prints FAIL <graph>: <problem> for each problem and exits 1; prints nothing for a graph without an inventory.
Python 3.9 or later, standard library only. Run: python3 scripts/inventory-check.py <graph dir>...
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys

RULES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "policy", "graph-rules.json")
PATH = re.compile(r"^[a-z0-9][a-z0-9-]*( [a-z0-9][a-z0-9-]*)*$")
TOP = {"tool", "release", "salt", "commands", "notCovered"}


def load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def key(entry, algo: str, salt: str):
    """The comparable form of one inventory entry: its digest, or None when it is neither a path nor a digest."""
    if isinstance(entry, str):
        return hashlib.new(algo, f"{salt}:{entry}".encode()).hexdigest() if PATH.match(entry) else None
    if isinstance(entry, dict) and isinstance(entry.get(algo), str) and re.fullmatch(r"[0-9a-f]{64}", entry[algo]):
        return entry[algo]
    return None


def check(d: str, rules: dict) -> list:
    cfg = rules["inventory"]
    inv_path = os.path.join(d, cfg["file"])
    if not os.path.exists(inv_path):
        return []
    try:
        inv = load(inv_path)
    except (OSError, ValueError):
        return [f"FAIL {d}: {cfg['file']} is not valid JSON"]
    if not isinstance(inv, dict) or set(inv) - TOP or not {"tool", "release", "commands"} <= set(inv):
        return [f"FAIL {d}: {cfg['file']} is an object with tool, release, commands and optionally salt and notCovered"]
    algo, vendor, tool = cfg["hash"], os.path.basename(d.rstrip("/")), inv["tool"]
    salt = inv.get("salt", "")
    problems = []
    if not isinstance(tool, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", tool) or not isinstance(salt, str):
        return [f"FAIL {d}: tool is a lower-case name and salt is text"]
    nodes = []
    for p in sorted(glob.glob(os.path.join(d, "graph", "nodes", "*.json"))):
        try:
            n = load(p)
        except (OSError, ValueError):
            continue
        if isinstance(n, dict) and isinstance(n.get("id"), str):
            nodes.append(n)
    releases = {n.get("attrs", {}).get("scope") for n in nodes if n.get("type") == cfg["releaseType"]}
    if inv["release"] not in releases:
        problems.append(f"the inventory's release {json.dumps(inv['release'])} is not the scope of a release node")
    prefix = f"{cfg['commandType']}.{vendor}.{tool}."
    covered = {}
    for n in nodes:
        if n.get("type") == cfg["commandType"] and n["id"].startswith(prefix):
            path = n["id"][len(prefix):].replace(".", " ")
            covered[key(path, algo, salt)] = n["id"]
    listed, seen = {}, set()
    for entry in inv["commands"] if isinstance(inv["commands"], list) else []:
        k = key(entry, algo, salt)
        if k is None:
            problems.append(f"a commands entry is neither a path nor a {algo} digest: {json.dumps(entry)}")
        elif k in seen:
            problems.append(f"a command is listed twice: {json.dumps(entry)}")
        else:
            seen.add(k)
            listed[k] = entry
    skipped = {}
    for entry in inv.get("notCovered", []):
        k = None
        if isinstance(entry, dict):
            k = key(entry["path"], algo, salt) if "path" in entry else key({algo: entry.get(algo)}, algo, salt)
        if k is None or not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            problems.append(f"a notCovered entry needs a path or digest and a reason: {json.dumps(entry)}")
        elif k not in listed:
            problems.append(f"a notCovered entry is not a listed command: {json.dumps(entry)}")
        elif k in covered:
            problems.append(f"{covered[k]} exists, yet its path is also in notCovered")
        else:
            skipped[k] = entry
    for k, entry in listed.items():
        if k not in covered and k not in skipped:
            problems.append(f"command {json.dumps(entry)} has no node and is not in notCovered")
    for k, node_id in covered.items():
        if k not in listed:
            problems.append(f"{node_id} is not a command of release {json.dumps(inv['release'])} in the inventory")
    return [f"FAIL {d}: {p}" for p in problems]


def main(dirs: list) -> int:
    rules = load(RULES)
    out = [line for d in dirs for line in check(d, rules)]
    for line in out:
        print(line)
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
