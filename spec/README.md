# Contracts

Each contract is a directory with `schema.json` (JSON Schema 2020-12), `examples/` that must pass and `counter-examples/` that must fail, each for one named reason. `scripts/contracts.sh` checks all of them, including the node schema of every domain. Code that reads or writes these files is generated from, or tested against, these schemas.

## refresh-report

The seam between public CI and the maintainer's machine.

1. A scheduled workflow in this repository reads one vendor graph at a commit, fetches each node's source (only hosts in `policy/sources.json`, redirects included) and looks for the node's quote in the page text. It writes a report and uploads it as a run artifact. It holds no secret and pushes nothing.
2. The PR opener on the maintainer's machine downloads the report, validates it against this schema and refuses one whose commit is not on main. It then opens pull requests as the organisation's app:
   - `unchanged`: one pull request bumping `measuredAt` and `attrs.fetched_at` of those nodes and nothing else. It may auto-merge through the allowlist.
   - `changed`: one pull request per node that records the finding in the vendor's `CHANGES.md` and does not touch the node. That path is outside the allowlist, so it waits for a maintainer; the corrected node is pushed to the same branch.
   - `unreadable`: no pull request; it stays in the report.

## sources

`policy/sources.json`: every host a node may cite, with its robots.txt verdict, the sentence of its terms that bears on automated reading, the page format and the request limits the fetcher obeys. Adding a host is a pull request that carries that evidence. A host whose robots.txt disallows us is not listed.

## Issue forms

`.github/ISSUE_TEMPLATE/fact-request.yml` asks for a new fact: the graph, the question, and optionally the source and quote. GitHub validates the form when it renders it; nothing runs on a new issue.
