# graphs

Sourced, machine-readable fact graphs, refreshed by workflows and merged only through checks.

## Layout

```
policy/
  constants.json           every pin (practice-library/.github: org.sha, release org.ref), runner, timeout, trusted author
                           and the gate's required jobs; the workflows, CODEOWNERS,
                           .github/required-checks.json and .github/automerge-paths.json are rendered from it
  sources.json             the hosts a source may name, with the evidence for each
  source-scopes.json       per host entry: approved paths, robots-disallowed paths, and whether permission is established
  graph-rules.json         what edges may join, which are acyclic or required (scripts/graph-semantics.py), and the lists
                           scripts/graph-check.sh and scripts/inventory-check.py read: statuses, the window separator,
                           which types a command line's nodes belong to, the inventory file name and its hash
  check.json               sources.json is checked against the pinned sources contract in policy/upstream/
templates/                 the files scripts/render.sh renders
spec/                      contracts shared by every domain
  refresh-report/          what the refresh workflow reports (schema, examples, counter-examples, check.json)
  sources/                 examples and counter-examples of the pinned sources contract
<domain>/                  one domain, one schema
  schema.json              the node contract for the domain: the shared node envelope plus its types
  examples/                nodes that must pass
  counter-examples/        nodes that must fail, one reason each
  check.json               examples must pass; each counter-example, on its own, must fail
  <vendor>/                one graph per vendor, such as vendors/github
    inventory.json         optional: the command paths of a CLI release, which command nodes must cover
  <jurisdiction>-<topic>/  under regulations/, one graph per topic, such as regulations/in-data-governance
    check.json             {"schema": "../schema.json", "instances": "graph/nodes"}
    graph/nodes/<id>.json  one fact per file
    INDEX.md               generated
    README.md              where the quotes come from, and their licence
```

Status: the contracts, checks and source policy exist, and there are vendor graphs under `vendors/`, each with a README naming its sources and their licence or terms. Every host they cite is in `policy/sources.json`, and `scripts/graph-check.sh` prints each graph's node count. The scheduled refresh workflow and the PR opener are planned (see `spec/README.md`).

The first domain is `vendors`: limits, plans, prices, access rules and terms of public services. A new domain is a new directory with its own `schema.json`; a new vendor is a new directory under its domain. Nothing else changes: every `check.json` is found and checked.

The second domain is `regulations`: dated rules from official legal texts, one graph per jurisdiction and topic. The first is `regulations/in-data-governance`: India's Digital Personal Data Protection Act, 2023 and Rules, 2025, and the CERT-In directions of 2022, from `egazette.gov.in` and `www.cert-in.org.in`. The second is `regulations/in-commercial-communications`: the Telecom Commercial Communications Customer Preference Regulations, 2018 and their amendments of 2018, 2025 and 2026, from `egazette.gov.in` only. The third is `regulations/in-gst-e-invoicing`: rule 48(4) of the CGST Rules, 2017 and the Central Tax notifications that set who must issue e-invoices, also from the Gazette only. Each README maps its graph's ten acceptance questions to the nodes that answer them.

The third and fourth domains are `languages` and `practices`, for the language root graphs (Java, Rust, Go) and for practice graphs; their schemas and checks exist, their content is not written yet. They are never auto-merged.

## A language fact

`languages/schema.json` uses the same envelope. A graph is `languages/<language>`, its ids are `<type>.<language>.<slug>` and its root node is `language.<language>`, which has no edges.
- **Types:** `release` (version in `attrs.scope`, date in `attrs.window`), `version-line`, `support-window` (the kind, such as LTS, in `attrs.scope`; the period in `attrs.window`, a date or `start/end`), `toolchain`, `module-system`, `edition`, `licence` (SPDX identifier in `attrs.scope`) and `compatibility-promise` (the promise quoted).
- **Edges:** `supersedes`, `supports`, `requires`, `partOf` and `introducedIn`.
- **Not used:** `attrs.status`, and every other relation.

`practices/schema.json` is kept minimal until v1.1: a `practice` root with `guideline` and `anti-pattern` nodes, joined by `partOf`, `requires`, `supersedes` and `appliesTo`.

Both domains have examples and counter-examples that `check.json` runs like the other domains', and `scripts/graph-check.sh` checks their graphs like vendor graphs: ids name the graph, one root node, edges inside the graph, source hosts listed.

## A regulation fact

`regulations/schema.json` uses the same envelope with its own types: `jurisdiction`, `authority`, `instrument`, `provision`, `obligation`, `timeline`, `penalty`, `definition` and `exemption`.
- **Ids:** `<type>.<jurisdiction>.<instrument>[.<part>]`, for example `provision.in.dpdp-rules-2025.r1-4`. The root node is `jurisdiction.<jurisdiction>`.
- **Applicability:** a provision, obligation, timeline, penalty or exemption that the text states carries:
  - `attrs.scope`: whom it applies to, in the text's own terms;
  - `attrs.window`: the date it applies from, or `start/end` for a period that is bounded or has ended (the end day is inclusive);
  - `attrs.status` on `measuredAt`: `in-force`, `notified-not-in-force`, `draft`, `superseded`, `expired` (ended by its own terms), `repealed` or `never-effective` (replaced before it commenced).
  A timeline or penalty also carries `value` and `unit`.
- **Publication:** a `publication` node (`publication.<jurisdiction>.<instrument>[.<part>]`) records the publication date in `attrs.window` (a single date) and the gazette issue in `attrs.scope`, `partOf` its instrument.
- **Edges:** `issuedBy`, `partOf`, `madeUnder`, `imposes`, `appliesTo`, `amends`, `supersedes` and `commencedBy`. A replacement is a `supersedes` edge from the new fact to each fact it replaces, so a split replacement is several edges to one target; the new fact's window says from when.
- **graph-check** (`scripts/graph-check.sh`) checks regulation graphs as it checks vendor graphs:
  - a regulation graph's directory is `<jurisdiction>-<topic>`, and its ids and root name that jurisdiction;
  - its hosts are listed in `policy/sources.json` under the directory name;
  - a status agrees with its window on `measuredAt`: `in-force` from the start on and not past the end, `notified-not-in-force` before the start, `expired` and `repealed` with an end before `measuredAt`, `never-effective` without an end; a window never ends before it starts;
  - a `superseded` or `never-effective` fact has a node that supersedes it, and a `supersedes` edge points at an ended fact (`superseded`, `expired`, `repealed` or `never-effective`) unless its source is still `notified-not-in-force` or `draft`. The lists are in `policy/graph-rules.json`.
- **No auto-merge:** `regulations/` is never auto-merged. `scripts/graphs.sh` lists only `vendors/` unless another domain is named, so no regulation path reaches the allowlist or loses its CODEOWNERS owner. Every change there is reviewed.

## A fact

Each fact is one JSON file named after its id, `<type>.<vendor>.<slug>`; a vendor's root node is `vendor.<vendor>`. It carries the official page it was read from, the time it was fetched and a short quote copied exactly from that page. A fact that cannot be confirmed is marked `unknown`, never guessed: its quote is the page's sentence nearest to the question, and its `note` says what could not be confirmed and why. When the page was checked and does not state the fact at all, the note starts with `Absent: ` and names that page; the schema rejects any other note that starts with the word absent. The shared envelope has had an `absent` verdict since practice-library/.github v2.1.0; `regulations/` forbids it and keeps this convention, and narrowing `vendors/` the same way is #44. A `denied` fact that rests on a feature list leaving the plan out says so in a note starting "Denied by exclusion from the quoted list".

`vendors/schema.json` is the organisation's shared fact-node envelope (`spec/node/schema.json` of practice-library/.github, which the schema check always resolves) with this domain's types and a few stricter rules: the id starts with its type, a price carries `value`, `unit` (currency included, for example `USD per million input tokens`) and `scope`, a vendor's root node has no edges, an `unknown` fact has a `note`, dates are real calendar dates and source hosts are lower-case names with a dot. A product or plan belongs to its vendor by its id and its directory. `scripts/graph-check.sh` checks what the schema cannot: each file is named after its id, the id names its vendor, the graph has one root node, every edge points at a node of the same graph, and every source's host is listed for that vendor in `policy/sources.json`.

Node types: `vendor`, `product`, `plan`, `price`, `limit`, `rate-limit`, `permission`, `rule`, `feature`, `term`, `release`, `capability`, and for a command line `command`, `flag`, `argument`, `configuration` and `error`. Edges, and no others: `availableOn`, `requires`, `grantedBy`, `limits`, `appliesTo`, `prohibitedBy`, `supersedes`, `partOf` (containment), and for versioned graphs `hasRelease` (product to release), `introducedIn` and `removedIn` (capability or command to release). `attrs.status` is not used in vendor graphs; it belongs to regulations.

A command line is typed: a `command` (`command.<vendor>.<tool>.<path words>`; `attrs.scope` its usage line, `attrs.quote` its summary) is `partOf` its parent command or the product; a `flag` (`attrs.scope` is `--name`; `value` and `unit` for a default or range) is `partOf` its command, or the product for a global flag; an `argument` is `partOf` its command; a `configuration` names a setting or environment variable in `attrs.scope`; an `error` is an error code, or an exit code with `value` and unit `exit-code`. Behaviour (what `--force` waives) stays a `rule` or `permission` with `appliesTo`. The relations `aliasOf`, `inherits`, `conflictsWith`, `raises`, `deprecatedIn` and `precedes` need the shared envelope to add them and are not used yet. `scripts/graph-check.sh` checks the `partOf` containment and, where a graph has `vendors/<vendor>/inventory.json`, coverage (`scripts/inventory-check.py`): the inventory names the `release` it lists, every listed command path has a `command` node or a `notCovered` entry with a reason, and every command node is listed. A path containing a denylisted word is stored as `{"sha256": <digest of salt:path>}`. A release names its version or model id in `attrs.scope` and, when stated, its date in `attrs.window` (YYYY-MM-DD); a release flagged breaking has a `note` starting with "Breaking". The shared envelope has no fields of its own for these.

## What may merge without review

Each vendor graph's `graph/nodes/` and `graph/refresh/` are on the auto-merge allowlist (`.github/automerge-paths.json`, which the organisation's auto-merge reads on the base commit) and have no CODEOWNERS owner; both lists are generated from `scripts/graphs.sh`, two entries per graph. A pull request touching only those paths must be a date bump: the required `bump-only` check accepts it only when every changed file is a modified node whose only changed lines are `measuredAt` and `attrs.fetched_at`, the new `measuredAt` is the date of the new `fetched_at`, `fetched_at` is later than before, and the pull request adds the refresh report (`graph/refresh/<run id>.json`) that shows the fetch (see `spec/README.md`). Each `INDEX.md` leaves the measurement dates out, so a bump leaves it unchanged. Adding, removing or changing a fact therefore fails `bump-only` unless the pull request also touches a path outside the allowlist, such as the vendor's `CHANGES.md`; such a pull request cannot auto-merge, so a maintainer reviews it. The index of every domain in `indexDomains` of `policy/constants.json` is checked, regulations included.

## Checks

Every pull request runs `.github/workflows/checks.yml`, which calls the reusable workflows of practice-library/.github at the release pinned in `policy/constants.json`. Its `discover` finds every tracked `check.json` and the schema check runs each target: a contract's `examples/` must pass, and with `each` every file in its `counter-examples/` must fail on its own, so an empty folder fails too. The leak scan runs on everything, and the gate passes only when its needs are exactly the jobs in `.github/required-checks.json`. Graphs-specific checks stay here: `scripts/render.sh --check` fails when a generated file differs from its template, `bump-only` and `graph-check` (below and above), and `scripts/selftest.sh` runs the cases under `selftest/` that show each script passing and failing where it should. Fixtures there keep their `check.json` as `_check.json`, so discovery never takes them for real targets. Two categories run `scripts/bump-only.sh` where it must fail: `bump-only-classify-fails/`, and `bump-only-pr/`, whose cases commit a `base/` and a `head/` tree in a temporary git repository before running `bump-only.sh pr`. A `graphs/` case may name a domain in a `domain` file. `render-allowlist/` renders `.github/automerge-paths.json` before and after a graph is added and prints the lines that changed: the file keeps each path and each comma on a line of its own, so adding a graph adds its own path line and changes no other entry's line. `guards` (`python3 scripts/guards.py`) mutates each row of its GUARDS and PINS tables and requires a named self-test case to fail. Each BACKSTOPS row, an early check that only gives a clearer message, must still fail with that check removed, because a later check catches the same input.

To change a pin, a runner, a trusted author or the gate's jobs, edit `policy/constants.json` and run `scripts/render.sh`; never edit a generated file. Dependabot (`.github/dependabot.yml`, the organisation's consumer template) proposes new pins; its pull request is finished by moving the pin into `policy/constants.json` and rendering.

This repository keeps no onboarding checklist: the settings, files and ruleset a repository of the organisation needs are applied by `scripts/onboard.sh` of practice-library/.github, following its `docs/new-repo-checklist.md`. The maintainers check a graph's edges and regenerate its `INDEX.md` locally with `et network check --graph vendors/<vendor>` and `et network index`; that tooling is not public, and CI does not depend on it.

## Licence

See `LICENSE`. Quoted text stays under its source's terms and is kept to short quotes with a link. Each vendor graph's `README.md` names where its quotes come from and under which licence, for example `vendors/github/README.md`.
