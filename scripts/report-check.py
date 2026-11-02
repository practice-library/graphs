"""A refresh report, held to the policy it was made under and to the node it is said to support.

  python3 scripts/report-check.py check <report> <sources.json> <source-scopes.json> <commit>
      Everything the report's schema cannot say, because it depends on policy/sources.json:
        - commit is the commit the run read (<commit>);
        - requests is the number of fetches and does not pass maxRequestsPerRun;
        - robots.txt of a host is fetched before any page, and from that host;
        - every fetch and every redirect hop is on a host listed for the graph's vendor, and no host's
          entry is unresolved in source-scopes.json (the run reads nothing from it);
        - no host gets more requests than its maxRequestsPerRun, and no response is longer than its maxBytes;
        - every host a page was fetched from has a robots record that allows it (allowed or absent), and a robots
          record that does not allow it ends the run: no page fetch and an aborted record;
        - a result's source was fetched, its finalUrl is where that fetch ended, and its time lies inside the run.
  python3 scripts/report-check.py bump <report> <old node> <new node>
      The date bump of one node is supported by the report: the report has an unchanged result for the node, for
      its source as the node names it, fetched at exactly the node's new attrs.fetched_at.
Prints FAIL <problem> for each and exits 1; prints nothing otherwise.
Python 3.9 or later, standard library only.
"""
from __future__ import annotations

import json
import sys
from urllib.parse import urlsplit


def load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def host_of(url: str) -> str:
    return urlsplit(url).hostname or ""


def check(report: dict, sources: dict, scopes: dict, commit: str) -> list:
    out = []
    if report.get("commit") != commit:
        out.append(f"FAIL commit {report.get('commit')} is not the commit {commit}")
    vendor = report["graph"].split("/", 1)[1]
    listed = {h["host"]: h for h in sources["hosts"] if h["vendor"] == vendor}
    unresolved = {s["host"] for s in scopes["entries"]
                  if s["vendor"] == vendor and s["permission"]["state"] == "unresolved"}
    fetches = report["fetches"]
    if report["requests"] != len(fetches):
        out.append(f"FAIL requests is {report['requests']} but the report lists {len(fetches)} fetches")
    if report["requests"] > sources["maxRequestsPerRun"]:
        out.append(f"FAIL requests {report['requests']} is over maxRequestsPerRun {sources['maxRequestsPerRun']}")
    seen_page = False
    per_host = {}
    for i, f in enumerate(fetches):
        h = host_of(f["url"])
        per_host[h] = per_host.get(h, 0) + 1
        if f["kind"] == "page":
            seen_page = True
        elif seen_page:
            out.append(f"FAIL fetch {i}: robots.txt of {h} is fetched after a page")
        if f["kind"] == "robots" and urlsplit(f["url"]).path != "/robots.txt":
            out.append(f"FAIL fetch {i}: {f['url']} is not the host's /robots.txt")
        for hop in [f["url"]] + f["redirects"]:
            if host_of(hop) not in listed:
                out.append(f"FAIL fetch {i}: {hop} is on a host not listed for {vendor}")
            elif host_of(hop) in unresolved:
                out.append(f"FAIL fetch {i}: {hop} is on a host whose permission is unresolved")
        entry = listed.get(h)
        if entry and f["bytes"] > entry["maxBytes"]:
            out.append(f"FAIL fetch {i}: {f['bytes']} bytes from {h} is over its maxBytes {entry['maxBytes']}")
    for h, n in sorted(per_host.items()):
        if h in listed and n > listed[h]["maxRequestsPerRun"]:
            out.append(f"FAIL {n} requests to {h} are over its maxRequestsPerRun {listed[h]['maxRequestsPerRun']}")
    robots = {r["host"]: r for r in report["robots"]}
    robots_fetched = {host_of(f["url"]) for f in fetches if f["kind"] == "robots"}
    for h in robots:
        if h not in robots_fetched:
            out.append(f"FAIL robots record for {h} has no robots.txt fetch")
    page_hosts = {host_of(f["url"]) for f in fetches if f["kind"] == "page"}
    for h in sorted(page_hosts):
        r = robots.get(h)
        if r is None or r["verdict"] not in ("allowed", "absent"):
            out.append(f"FAIL pages were fetched from {h} without a robots record that allows it")
    if any(r["verdict"] not in ("allowed", "absent") for r in robots.values()):
        if page_hosts:
            out.append("FAIL a robots.txt did not allow the run, yet pages were fetched")
        if "aborted" not in report:
            out.append("FAIL a robots.txt did not allow the run, yet the report is not aborted")
    pages = {f["url"]: f for f in fetches if f["kind"] == "page"}
    for res in report["results"]:
        f = pages.get(res["source"])
        if f is None:
            out.append(f"FAIL {res['node']}: its source {res['source']} was not fetched")
            continue
        final = f["redirects"][-1] if f["redirects"] else f["url"]
        if "finalUrl" in res and res["finalUrl"] != final:
            out.append(f"FAIL {res['node']}: finalUrl {res['finalUrl']} is not where the fetch ended, {final}")
        if res.get("httpStatus") != f.get("httpStatus"):
            out.append(f"FAIL {res['node']}: httpStatus {res.get('httpStatus')} differs from the fetch's {f.get('httpStatus')}")
        if not report["run"]["startedAt"] <= res["fetchedAt"] <= report["run"]["finishedAt"]:
            out.append(f"FAIL {res['node']}: fetchedAt {res['fetchedAt']} is outside the run")
    return out


def bump(report: dict, old: dict, new: dict) -> list:
    out = []
    mine = [r for r in report["results"] if r["node"] == new.get("id")]
    if len(mine) != 1:
        return [f"FAIL the report has {len(mine)} results for {new.get('id')}, not one"]
    r = mine[0]
    if r["outcome"] != "unchanged":
        out.append(f"FAIL {new['id']}: the report's outcome is {r['outcome']}, not unchanged")
    if r["source"] != new.get("source"):
        out.append(f"FAIL {new['id']}: the report read {r['source']}, the node cites {new.get('source')}")
    if r["fetchedAt"] != (new.get("attrs") or {}).get("fetched_at"):
        out.append(f"FAIL {new['id']}: fetched_at is not the report's fetchedAt {r['fetchedAt']}")
    if r.get("claim", "point") != "point" and "query" not in r:
        out.append(f"FAIL {new['id']}: a {r['claim']} claim is not refreshed without a query")
    return out


def main(argv: list) -> int:
    try:
        if argv[0] == "check" and len(argv) == 5:
            out = check(load(argv[1]), load(argv[2]), load(argv[3]), argv[4])
        elif argv[0] == "bump" and len(argv) == 4:
            out = bump(load(argv[1]), load(argv[2]), load(argv[3]))
        else:
            print(__doc__)
            return 2
    except (OSError, ValueError, KeyError, TypeError, IndexError) as e:
        print(f"FAIL unreadable input: {e!r}")
        return 1
    for line in out:
        print(line)
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
