# graphs

Sourced, machine-readable fact graphs, refreshed by workflows and merged only through checks.

## Layout

```
policy/
  constants.json           every pin (practice-library/.github at v1.0.0), runner, timeout, trusted author
                           and the gate's required jobs; the workflows, CODEOWNERS,
                           .github/required-checks.json and .github/automerge-paths.json are rendered from it
  sources.json             the hosts a source may name, with the evidence for each (none yet)
  check.json               sources.json is checked against spec/sources
templates/                 the files scripts/render.sh renders
spec/                      contracts shared by every domain
  refresh-report/          what the refresh workflow reports (schema, examples, counter-examples, check.json)
  sources/                 the source policy
<domain>/                  one domain, one schema
  schema.json              the node contract for the domain: the shared node envelope plus its types
  examples/                nodes that must pass
  counter-examples/        nodes that must fail, one reason each
  check.json               examples must pass; each counter-example, on its own, must fail
  <vendor>/                planned: one graph per vendor; none exists yet
    check.json             {"schema": "../schema.json", "instances": "graph/nodes"}
    graph/nodes/<id>.json  one fact per file
    INDEX.md               generated
```

Status: the contracts, checks and source policy exist. No vendor graph exists yet, `policy/sources.json` lists no host yet, and the scheduled refresh workflow and the PR opener are planned (see `spec/README.md`).

The first domain is `vendors`: limits, plans, prices, access rules and terms of public services. A new domain is a new directory with its own `schema.json`; a new vendor is a new directory under its domain. Nothing else changes: every `check.json` is found and checked.

## A fact

Each fact is one JSON file named after its id, `<type>.<vendor>.<slug>`; a vendor's root node is `vendor.<vendor>`. It carries the official page it was read from, the time it was fetched and a short quote copied exactly from that page. A fact that cannot be confirmed is marked `unknown`, never guessed: its quote is the page's sentence nearest to the question, and its `note` says what could not be confirmed and why.

`vendors/schema.json` is the organisation's shared fact-node envelope (`spec/node/schema.json` of practice-library/.github, which the schema check always resolves) with this domain's types and a few stricter rules: the id starts with its type, a price carries `value`, `unit` (currency included, for example `USD per million input tokens`) and `scope`, a vendor's root node has no edges, an `unknown` fact has a `note`, dates are real calendar dates and source hosts are lower-case names with a dot. A product or plan belongs to its vendor by its id and its directory. `scripts/graph-check.sh` checks what the schema cannot: each file is named after its id, the id names its vendor, the graph has one root node, every edge points at a node of the same graph, and every source's host is listed for that vendor in `policy/sources.json`.

Node types: `vendor`, `product`, `plan`, `price`, `limit`, `rate-limit`, `permission`, `rule`, `feature`, `term`. Edges: `availableOn`, `requires`, `grantedBy`, `limits`, `appliesTo`, `prohibitedBy`, `supersedes`.

## What may merge without review

Each vendor graph's `graph/nodes/` is on the auto-merge allowlist (`.github/automerge-paths.json`, which the organisation's auto-merge reads on the base commit) and has no CODEOWNERS owner; both lists are generated from `scripts/graphs.sh`, one entry per graph. A pull request touching only those paths must be a date bump: the required `bump-only` check accepts it only when every changed file is a modified node whose only changed lines are `measuredAt` and `attrs.fetched_at`, the new `measuredAt` is the date of the new `fetched_at`, and `fetched_at` is later than before. Adding, removing or changing a fact therefore also adds a line to that vendor's `CHANGES.md`, which is outside the allowlist, so a maintainer reviews it.

## Checks

Every pull request runs `.github/workflows/checks.yml`, which calls the reusable workflows of practice-library/.github v1.0.0. Its `discover` finds every tracked `check.json` and the schema check runs each target: a contract's `examples/` must pass, and with `each` every file in its `counter-examples/` must fail on its own, so an empty folder fails too. The leak scan runs on everything, and the gate passes only when its needs are exactly the jobs in `.github/required-checks.json`. Graphs-specific checks stay here: `scripts/render.sh --check` fails when a generated file differs from its template, `bump-only` and `graph-check` (below and above), and `scripts/selftest.sh` runs the cases under `selftest/` that show each script passing and failing where it should. Fixtures there keep their `check.json` as `_check.json`, so discovery never takes them for real targets.

To change a pin, a runner, a trusted author or the gate's jobs, edit `policy/constants.json` and run `scripts/render.sh`; never edit a generated file. Dependabot (`.github/dependabot.yml`, the organisation's consumer template) proposes new pins; its pull request is finished by moving the pin into `policy/constants.json` and rendering.

This repository keeps no onboarding checklist: the settings, files and ruleset a repository of the organisation needs are applied by `scripts/onboard.sh` of practice-library/.github, following its `docs/new-repo-checklist.md`. Once a vendor graph exists, `et network check --graph vendors/<vendor>` checks its edges and its `INDEX.md` locally; today it fails, because there is no vendor graph and so no node to load.

## Licence

See `LICENSE`. Quoted text stays under its source's terms and is kept to short quotes with a link.
