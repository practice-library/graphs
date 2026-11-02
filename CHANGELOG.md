# Changelog

One entry per release of this repository. A release names the practice-library/.github release its own CI checked it against.

## v1.0.0

Checked against practice-library/.github v3.1.0 (`fa14c82916585c4e3357985a0433e60123f3b91d`). No backward compatibility with v0.2.0 is kept: the vendor schema, the regulation schema and the sources policy all change shape.

- `languages/`, a new domain with three root graphs, each with a README that maps ten acceptance questions to nodes: `languages/go` (59 nodes, from go.dev; #96), `languages/java` (41 nodes, from openjdk.org; #95, #97) and `languages/rust` (51 nodes, from rust-lang.org and its subdomains; #97). `practices/` is a declared graph kind with no graph yet. The openjdk.org terms bar automated reading without written permission. The Java pages were nevertheless read once by an automated agent (2026-11-02), and the maintainers chose to publish the facts with that statement in `languages/java/README.md`. Permission is recorded as `unresolved`, and a refresh reads nothing from the host.
- `vendors/schema.json` (#93): the node types `command`, `flag`, `argument`, `configuration` and `error` for a command-line tool, with `scripts/inventory-check.py` checking a vendor's `inventory.json` coverage; `edges[].rel` is limited to the vendor relations plus `partOf`; `attrs.status` and the envelope's `absent` verdict are forbidden (#44, #84).
- `regulations/schema.json` (#93): a node's `window` may be an interval, and a regulation may be `expired`, `repealed` or `never-effective`; the node type `publication` (with `scope` and a single-date `window`) is new; the thirty-day upload limit of October 2020 is its own `expired` timeline node; `supersedes` links are completed (#75, #76).
- Checks (#94): `scripts/graph-semantics.py` and `policy/graph-rules.json` check relation endpoints, loops, provenance and supersession (#77); every domain in `indexDomains` is indexed and checked (#78); a date bump needs the refresh report that shows its fetch, and `INDEX.md` carries no measurement dates (#69, #79); `policy/source-scopes.json` is new and required: every host in `policy/sources.json` needs a scope there, which limits it to approved paths and records whether permission is established (#80, #83); robots refusals and throttles are verdicts of the refresh report, with `fetches` provenance checked by `scripts/report-check.py` (#81, #82); `spec/sources/schema.json` is removed in favour of the pinned upstream copy (#58).
- Six `vendors/temporal` quotes that had left their pages are re-quoted (#102).

Also in this release:

- Pins practice-library/.github v3.1.0 (`fa14c82916585c4e3357985a0433e60123f3b91d`), after v2.6.0, taking in the breaking changes of v3.0.0. Every reusable workflow call in `.github/workflows/` moves to that commit, rendered from `policy/constants.json`.
- The guards check out their own tooling at the pinned commit. A loosened schema, or a denylist exemption that is added or widened, now needs a maintainer's approval of the pull request's exact head; the `schema-loosening-approved` label only re-runs the check.
- The pinned sources contract moves to `policy/upstream/practice-library-.github/v3.1.0/`, an unchanged copy of the file at that commit (the same blob as at v3.0.0), and `policy/check.json` resolves it there. At v3.0.0 a host's `terms` may carry an optional `note` (at most 300 characters) for terms with no clause on automated reading.
- No caller input or required job changes: the caller keeps the same inputs, the required check is still `gate / gate`, and this repository used none of the paths, inputs or constants that v3.0.0 removed.
- Checks run for pull requests to, and pushes to, the `v1` integration branch as well as `main`.
- The `guards` job runs as six shards, with check names `guards 1/6` to `guards 6/6`; `scripts/guards.py --shard K/N` selects the rows of one shard, and the gate needs the whole matrix.
- `regulations/schema.json` no longer restates the envelope's `attrs.status` list; the pinned envelope owns it.
- The shared node contract at v3.1.0 allows the statuses `expired`, `repealed` and `never-effective`, which the regulation graphs use; at v3.1.0 the `schema-loosening` guard also judges in a calling repository such as this one.
- `policy/sources.json`: `docs.github.com` may serve up to 4000000 bytes per page, up from 2000000. The workflow syntax reference measured 2105922 bytes on 2026-11-02 and could not be re-read under the old cap.
- Each `INDEX.md` header names its generator, `scripts/index.sh`, instead of `node bin/index.mjs`; every index is regenerated, a data-only change. The README names the public scripts that check the graphs and regenerate the indexes.

## v0.2.0

Checked against practice-library/.github v2.4.0 (`75a03317883e16f7ad93f1239dc53c9d0e1c4cc1`).

- Pins practice-library/.github v2.4.0 (#43), after v2.1.0 (#32). Through the shared node envelope, `vendors/schema.json` now also accepts `attrs.status` and the six legal-text edge relations; narrowing it again is #44. The required checks gain the four guard jobs: denylist, removed-paths, release-note and schema-loosening. The sources contract is checked against its upstream copy, with examples and counter-examples.
- `vendors/temporal`: Temporal Server releases with breaking flags and capabilities, and Temporal Cloud limits, plans, prices and included allocations; 65 nodes (#34).
- `.github/automerge-paths.json` keeps one path per line, so adding a graph adds only its own line (#38).
- README names the `guards` check and the new self-test categories (#31).

## v0.1.0

The first release: the contracts, checks and source policy, and the first two vendor graphs.
