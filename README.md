# graphs

Sourced, machine-readable fact graphs, refreshed by workflows and merged only through checks.

## Layout

```
policy/
  constants.json           every pin, runner, timeout and trusted author; the workflows are rendered from it
  sources.json             the hosts a source may name, with the evidence for each
  check.json               sources.json is checked against spec/sources
templates/                 the workflows and CODEOWNERS, rendered by scripts/render.sh
spec/                      contracts shared by every domain
  refresh-report/          what the refresh workflow reports (schema, examples, counter-examples)
  sources/                 the source policy
<domain>/                  one domain, one schema
  schema.json              the node contract for the domain
  examples/                nodes that must pass
  counter-examples/        nodes that must fail, one reason each
  <vendor>/                one graph per vendor
    check.json             {"schema": "../schema.json", "instances": "graph/nodes"}
    graph/nodes/<id>.json  one fact per file
    INDEX.md               generated
```

The first domain is `vendors`: limits, plans, prices, access rules and terms of the services we depend on. A new domain is a new directory with its own `schema.json`; a new vendor is a new directory under its domain. Nothing else changes: every `check.json` is found and checked.

## A fact

Each fact is one JSON file named after its id, `<type>.<vendor>.<slug>`; a vendor's root node is `vendor.<vendor>`. It carries the official page it was read from, the time it was fetched and a short quote copied exactly from that page. A fact that cannot be confirmed is marked `unknown`, never guessed. Edges stay inside one vendor's graph.

## What may merge without review

Each vendor graph's `graph/nodes/` is on the auto-merge allowlist and has no CODEOWNERS owner; both lists are generated from `scripts/graphs.sh`, one entry per graph. A pull request touching only those paths must be a date bump: the required `bump-only` check accepts it only when every changed file is a modified node whose only changed lines are `measuredAt` and `attrs.fetched_at`, the new `measuredAt` is the date of the new `fetched_at`, and `fetched_at` is later than before. Adding, removing or changing a fact therefore also adds a line to that vendor's `CHANGES.md`, which is outside the allowlist, so a maintainer reviews it.

Node types: `vendor`, `product`, `plan`, `price`, `limit`, `rate-limit`, `permission`, `rule`, `feature`, `term`. Edges: `offeredBy`, `availableOn`, `requires`, `grantedBy`, `limits`, `appliesTo`, `prohibitedBy`, `supersedes`.

## Checks

Every pull request runs `.github/workflows/checks.yml`. `scripts/discover.sh` lists what the organisation's schema check runs on: every `check.json`, every contract's `examples/` (must pass) and each of its `counter-examples/` (must fail). The leak scan runs on everything, `scripts/render.sh --check` fails when a generated file differs from its template, and `scripts/selftest.sh` runs the cases under `selftest/` that show each script passing and failing where it should. A contract without at least one example and one counter-example fails discovery.

To change a pin, a runner or a trusted author, edit `policy/constants.json` and run `scripts/render.sh`; never edit a generated file. Locally, `et network check --graph vendors/<vendor>` checks a graph's edges and its `INDEX.md`.

## Licence

See `LICENSE`. Quoted text stays under its source's terms and is kept to short quotes with a link.
