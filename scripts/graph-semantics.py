"""What a graph's edges mean, not only where they point.

For each <graph dir>/graph/nodes/*.json, under the rules of one domain in policy/graph-rules.json:
  - an edge may not point a node at itself, and the node it points at must exist;
  - the types at its two ends must be a pair the relation lists (an issuedBy edge cannot end at a timeline);
  - relations the rules name as acyclic form no loop (a replacement chain that returns to its start);
  - a type with a required edge carries between min and max edges of that relation to the named type
    (a duty without partOf, an instrument without issuedBy), unless the node's attribute is one of the
    rule's `unless` values or its id is one of the rule's `exceptions` (gaps in the content, listed in
    policy/graph-rules.json until the content closes them);
  - supersession: a node that a supersedes edge replaces, and that carries a status, has an ended status
    (superseded, expired, repealed, never-effective) unless the replacing node is still pending. The reverse is not required: a repeal leaves a superseded node with no replacement;
  - containment: the id of a contained node continues the id of the node its partOf edge names
    (provision.in.act-2018.r5 is part of instrument.in.act-2018).
Prints FAIL <id>: <problem> for each and exits 1; prints nothing otherwise. A node file that is not JSON is
left to graph-check.sh, which reports it.
Python 3.9 or later, standard library only.
Run: python3 scripts/graph-semantics.py <rules.json> <domain> <graph dir>...
"""
from __future__ import annotations

import glob
import json
import os
import sys


def load(d: str) -> dict:
    nodes = {}
    for path in sorted(glob.glob(os.path.join(d, "graph", "nodes", "*.json"))):
        try:
            with open(path, encoding="utf-8") as f:
                n = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(n, dict) and isinstance(n.get("id"), str):
            nodes[n["id"]] = n
    return nodes


def edges(n: dict) -> list:
    return [e for e in (n.get("edges") or []) if isinstance(e, dict)]


def tail(i: str) -> list:
    return i.split(".")[2:]


def cycle(rel: str, nodes: dict):
    """The ids of one loop of rel edges, or None."""
    nxt = {i: [e.get("to") for e in edges(n) if e.get("rel") == rel and e.get("to") in nodes] for i, n in nodes.items()}
    state = {}
    stack = []

    def visit(i):
        state[i] = 1
        stack.append(i)
        for j in nxt[i]:
            if state.get(j) == 1:
                return stack[stack.index(j):] + [j]
            if j not in state:
                found = visit(j)
                if found:
                    return found
        stack.pop()
        state[i] = 2
        return None

    for i in sorted(nodes):
        if i not in state:
            found = visit(i)
            if found:
                return found
    return None


def problems(rules: dict, nodes: dict) -> list:
    out = []
    rel_pairs = {r: {tuple(p) for p in pairs} for r, pairs in rules.get("relations", {}).items()}
    for i, n in sorted(nodes.items()):
        for e in edges(n):
            rel, to = e.get("rel"), e.get("to")
            if to == i:
                out.append(f"FAIL {i}: edge {rel} points at the node itself")
                continue
            if to not in nodes:
                continue  # a dangling edge is graph-check.sh's report
            if rel not in rel_pairs:
                out.append(f"FAIL {i}: relation {rel} is not in policy/graph-rules.json")
            elif (n.get("type"), nodes[to].get("type")) not in rel_pairs.get(rel, set()):
                out.append(f"FAIL {i}: edge {rel} joins a {n.get('type')} to {to}, a {nodes[to].get('type')}, which {rel} does not allow")
    for rel in rules.get("acyclic", []):
        loop = cycle(rel, nodes)
        if loop:
            out.append(f"FAIL {loop[0]}: {rel} edges form a loop: {' -> '.join(loop)}")
    for req in rules.get("required", []):
        for i, n in sorted(nodes.items()):
            if n.get("type") != req["type"] or i in req.get("exceptions", []):
                continue
            skip = req.get("unless")
            if skip and (n.get("attrs") or {}).get(skip["attr"]) in skip["in"]:
                continue
            count = sum(1 for e in edges(n) if e.get("rel") == req["rel"] and e.get("to") in nodes
                        and nodes[e["to"]].get("type") == req["to"])
            if count < req.get("min", 0):
                out.append(f"FAIL {i}: a {req['type']} needs {req.get('min', 0)} {req['rel']} edge to a {req['to']}, it has {count}")
            elif count > req.get("max", count):
                out.append(f"FAIL {i}: a {req['type']} has {count} {req['rel']} edges to a {req['to']}, at most {req['max']} allowed")
    sup = rules.get("supersession")
    if sup:
        for i, n in sorted(nodes.items()):
            for e in edges(n):
                if e.get("rel") != sup["rel"] or e.get("to") not in nodes or e["to"] == i:
                    continue
                old = nodes[e["to"]]
                status = (old.get("attrs") or {}).get(sup["attr"])
                replaced = sup["replaced"] if isinstance(sup["replaced"], list) else [sup["replaced"]]
                if (n.get("attrs") or {}).get(sup["attr"]) in sup.get("pendingReplacers", []):
                    continue  # a replacement not yet in force leaves the old node as it is
                if status is not None and status not in replaced:
                    out.append(f"FAIL {e['to']}: replaced by {i} but its {sup['attr']} is {status}, not {' or '.join(replaced)}")
    con = rules.get("containment")
    if con:
        for i, n in sorted(nodes.items()):
            if n.get("type") == con["to"]:
                continue
            for e in edges(n):
                if e.get("rel") != con["rel"] or e.get("to") not in nodes or nodes[e["to"]].get("type") != con["to"]:
                    continue
                if tail(i)[:len(tail(e["to"]))] != tail(e["to"]) or len(tail(i)) <= len(tail(e["to"])):
                    out.append(f"FAIL {i}: its id does not continue {e['to']}, the {con['to']} it is part of")
    return out


def main(argv: list) -> int:
    with open(argv[0], encoding="utf-8") as f:
        rules = json.load(f)[argv[1]]
    failed = 0
    for d in argv[2:]:
        nodes = load(d)
        for line in problems(rules, nodes):
            print(line)
            failed = 1
    return failed


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
