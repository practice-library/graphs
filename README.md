# graphs

Sourced, machine-readable fact graphs, refreshed by workflows and merged only through checks.

## Layout

```
spec/                      contracts shared by every domain
  refresh-report/          what the refresh workflow reports (schema, examples, counter-examples)
  sources/                 the hosts a source may name and the evidence for each
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

Node types: `vendor`, `product`, `plan`, `price`, `limit`, `rate-limit`, `permission`, `rule`, `feature`, `term`. Edges: `offeredBy`, `availableOn`, `requires`, `grantedBy`, `limits`, `appliesTo`, `prohibitedBy`, `supersedes`.

## Checks

Every pull request runs `.github/workflows/gate.yml`: each `check.json` through the organisation's schema check, every contract's counter-examples (which must fail), and the leak scan. Locally:

```sh
scripts/contracts.sh <path to jsonschema 17.2.1>
et network check --graph vendors/<vendor>
```

## Licence

See `LICENSE`. Quoted text stays under its source's terms and is kept to short quotes with a link.
