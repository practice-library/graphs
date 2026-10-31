# graphs

Sourced, machine-readable fact graphs, refreshed by workflows and merged only through checks.

## Layout

```
policy/
  constants.json           every pin, runner, timeout and trusted author; the workflows are rendered from it
  sources.json             the hosts a source may name, with the evidence for each (none yet)
  check.json               sources.json is checked against spec/sources
templates/                 the workflows and CODEOWNERS, rendered by scripts/render.sh
spec/                      contracts shared by every domain
  refresh-report/          what the refresh workflow reports (schema, examples, counter-examples)
  sources/                 the source policy
<domain>/                  one domain, one schema
  schema.json              the node contract for the domain
  examples/                nodes that must pass
  counter-examples/        nodes that must fail, one reason each
  <vendor>/                planned: one graph per vendor; none exists yet
    check.json             {"schema": "../schema.json", "instances": "graph/nodes"}
    graph/nodes/<id>.json  one fact per file
    INDEX.md               generated
```

Status: the contracts, checks and source policy exist. No vendor graph exists yet, `policy/sources.json` lists no host yet, and the scheduled refresh workflow and the PR opener are planned (see `spec/README.md`).

The first domain is `vendors`: limits, plans, prices, access rules and terms of the services we depend on. A new domain is a new directory with its own `schema.json`; a new vendor is a new directory under its domain. Nothing else changes: every `check.json` is found and checked.

## A fact

Each fact is one JSON file named after its id, `<type>.<vendor>.<slug>`; a vendor's root node is `vendor.<vendor>`. It carries the official page it was read from, the time it was fetched and a short quote copied exactly from that page. A fact that cannot be confirmed is marked `unknown`, never guessed: it then carries no quote, and its `note` says what could not be confirmed and why. `scripts/graph-check.sh` checks what the schema cannot: each file is named after its id, the id names its vendor, the graph has one root node, every edge points at a node of the same graph, and every source's host is listed for that vendor in `policy/sources.json`.

Node types: `vendor`, `product`, `plan`, `price`, `limit`, `rate-limit`, `permission`, `rule`, `feature`, `term`. Edges: `offeredBy`, `availableOn`, `requires`, `grantedBy`, `limits`, `appliesTo`, `prohibitedBy`, `supersedes`.

## What may merge without review

Each vendor graph's `graph/nodes/` is on the auto-merge allowlist and has no CODEOWNERS owner; both lists are generated from `scripts/graphs.sh`, one entry per graph. A pull request touching only those paths must be a date bump: the required `bump-only` check accepts it only when every changed file is a modified node whose only changed lines are `measuredAt` and `attrs.fetched_at`, the new `measuredAt` is the date of the new `fetched_at`, and `fetched_at` is later than before. Adding, removing or changing a fact therefore also adds a line to that vendor's `CHANGES.md`, which is outside the allowlist, so a maintainer reviews it.

## Checks

Every pull request runs `.github/workflows/checks.yml`. `scripts/discover.sh` lists what the organisation's schema check runs on: every `check.json`, every contract's `examples/` (must pass) and each of its `counter-examples/` (must fail). The leak scan runs on everything, `scripts/render.sh --check` fails when a generated file differs from its template, and `scripts/selftest.sh` runs the cases under `selftest/` that show each script passing and failing where it should. A contract without at least one example and one counter-example fails discovery.

To change a pin, a runner or a trusted author, edit `policy/constants.json` and run `scripts/render.sh`; never edit a generated file. Once a vendor graph exists, `et network check --graph vendors/<vendor>` checks its edges and its `INDEX.md` locally; today it fails, because there is no vendor graph and so no node to load.

## Licence

See `LICENSE`. Quoted text stays under its source's terms and is kept to short quotes with a link.
