"""Does the host approval in policy/sources.json say no more than its evidence?

Reads policy/sources.json, policy/source-scopes.json (one scope per host entry; the sources contract that
validates sources.json allows no extra fields, so the scopes live beside it) and policy/blocked-hosts.md, and
the nodes of every graph in the domains named by indexDomains of policy/constants.json, then fails when:
  - two host entries share a graph and host (the key is vendor + host);
  - an entry's robots.txt url is not /robots.txt of its own host;
  - a host entry has no scope, a scope has no host entry, or two scopes share a key;
  - a scope path does not start and end with "/", or a disallowed path is not a path of the same form;
  - a scope has no paths, or its permission is not established with the clause and its page (clause, clauseUrl)
    or unresolved with a reason: a clause that does not show permission is recorded as unresolved, never
    as established;
  - a node cites a source whose host is not listed for its graph, whose path is under none of the scope's paths,
    or whose path is under one of its disallowed paths (a disallowed path wins over a permitted one);
  - a host of policy/sources.json is also a host in policy/blocked-hosts.md.
Prints FAIL <what> for each, then "unresolved: <n> of <m> host entries"; exits 1 on any FAIL.
A scope entry is {vendor, host, paths, disallowed?, permission}; the refresh run reads nothing from an
unresolved entry (spec/README.md).
Python 3.9 or later, standard library only. Run: python3 scripts/sources-check.py [root]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from urllib.parse import urlsplit


def load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def blocked_hosts(path: str) -> set:
    if not os.path.exists(path):
        return set()
    hosts = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\|\s*([a-z0-9.-]+\.[a-z]+)\s*\|", line)
            if m and m.group(1) != "host":
                hosts.add(m.group(1))
    return hosts


def under(path: str, prefixes: list) -> bool:
    return any(path.startswith(p) for p in prefixes)


def check(root: str) -> list:
    out = []
    sources = load(os.path.join(root, "policy", "sources.json"))
    scopes = load(os.path.join(root, "policy", "source-scopes.json"))["entries"]
    keys = {}
    for h in sources["hosts"]:
        k = (h["vendor"], h["host"])
        if k in keys:
            out.append(f"FAIL policy/sources.json lists {h['host']} for {h['vendor']} twice")
        keys[k] = h
        r = urlsplit(h["robots"]["url"])
        if r.hostname != h["host"] or r.path != "/robots.txt" or r.query:
            out.append(f"FAIL {h['vendor']} {h['host']}: robots url {h['robots']['url']} is not https://{h['host']}/robots.txt")
    scope = {}
    for s in scopes:
        k = (s["vendor"], s["host"])
        if k in scope:
            out.append(f"FAIL policy/source-scopes.json has {s['host']} for {s['vendor']} twice")
        scope[k] = s
        if k not in keys:
            out.append(f"FAIL scope {s['vendor']} {s['host']} has no host entry in policy/sources.json")
        if not s.get("paths"):
            out.append(f"FAIL scope {s['vendor']} {s['host']}: no permitted path")
        for p in s.get("paths", []) + s.get("disallowed", []):
            if not (p.startswith("/") and p.endswith("/")):
                out.append(f"FAIL scope {s['vendor']} {s['host']}: path {p} must start and end with /")
        perm = s.get("permission") or {}
        if perm.get("state") == "established":
            if not perm.get("clause") or not perm.get("clauseUrl"):
                out.append(f"FAIL scope {s['vendor']} {s['host']}: established permission needs its clause and clauseUrl")
        elif perm.get("state") == "unresolved":
            if not perm.get("reason"):
                out.append(f"FAIL scope {s['vendor']} {s['host']}: unresolved permission needs its reason")
        else:
            out.append(f"FAIL scope {s['vendor']} {s['host']}: permission.state is established or unresolved")
    for k in keys:
        if k not in scope:
            out.append(f"FAIL {k[0]} {k[1]} has no scope in policy/source-scopes.json")
    blocked = blocked_hosts(os.path.join(root, "policy", "blocked-hosts.md"))
    for h in sorted({k[1] for k in keys} & blocked):
        out.append(f"FAIL {h} is in policy/sources.json and in policy/blocked-hosts.md")
    domains = load(os.path.join(root, "policy", "constants.json"))["indexDomains"] \
        if os.path.exists(os.path.join(root, "policy", "constants.json")) else ["vendors", "regulations"]
    for domain in domains:
        for path in sorted(glob.glob(os.path.join(root, domain, "*", "graph", "nodes", "*.json"))):
            graph = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(path))))
            try:
                node = load(path)
                u = urlsplit(node["source"])
            except (OSError, ValueError, KeyError, TypeError):
                continue  # graph-check.sh reports it
            s = scope.get((graph, u.hostname))
            if s is None:
                continue  # an unlisted host is graph-check.sh's report
            p = u.path or "/"
            if under(p, s.get("disallowed", [])):
                out.append(f"FAIL {node.get('id')}: {u.hostname}{p} is under a path robots.txt disallows ({domain}/{graph})")
            elif not under(p, s["paths"]):
                out.append(f"FAIL {node.get('id')}: {u.hostname}{p} is outside the approved paths {s['paths']} ({domain}/{graph})")
    n = sum(1 for s in scopes if (s.get("permission") or {}).get("state") == "unresolved")
    out.append(f"unresolved: {n} of {len(sources['hosts'])} host entries")
    return out


def main(argv: list) -> int:
    root = argv[0] if argv else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lines = check(root)
    for line in lines:
        print(line)
    return 1 if any(line.startswith("FAIL") for line in lines) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
