# Changelog

One entry per release of this repository. A release names the practice-library/.github release its own CI checked it against.

## Unreleased

- Pins practice-library/.github v3.1.0 (`fa14c82916585c4e3357985a0433e60123f3b91d`), after v2.6.0, taking in the breaking changes of v3.0.0. Every reusable workflow call in `.github/workflows/` moves to that commit, rendered from `policy/constants.json`.
- The guards check out their own tooling at the pinned commit. A loosened schema, or a denylist exemption that is added or widened, now needs a maintainer's approval of the pull request's exact head; the `schema-loosening-approved` label only re-runs the check.
- The pinned sources contract moves to `policy/upstream/practice-library-.github/v3.1.0/`, an unchanged copy of the file at that commit (the same blob as at v3.0.0), and `policy/check.json` resolves it there. At v3.0.0 a host's `terms` may carry an optional `note` (at most 300 characters) for terms with no clause on automated reading.
- No caller input or required job changes: the caller keeps the same inputs, the required check is still `gate / gate`, and this repository used none of the paths, inputs or constants that v3.0.0 removed.
- Checks run for pull requests to, and pushes to, the `v1` integration branch as well as `main`.
- The `guards` job runs as six shards, with check names `guards 1/6` to `guards 6/6`; `scripts/guards.py --shard K/N` selects the rows of one shard, and the gate needs the whole matrix.
- `languages`: the edge relation `supports`, which the shared node envelope does not have, is replaced by the envelope's `appliesTo` in `languages/schema.json`, the `languages/go` nodes, the examples and the counter-examples. A consumer that reads language edges by relation reads `appliesTo`.
- `regulations/schema.json` no longer restates the envelope's `attrs.status` list; the pinned envelope owns it.
- The shared node contract at v3.1.0 allows the statuses `expired`, `repealed` and `never-effective`, which the regulation graphs use; at v3.1.0 the `schema-loosening` guard also judges in a calling repository such as this one.
- `policy/sources.json`: `docs.github.com` may serve up to 4000000 bytes per page, up from 2000000. The workflow syntax reference measured 2105922 bytes on 2026-11-02 and could not be re-read under the old cap.
- Each `INDEX.md` header names its generator, `scripts/index.sh`, instead of `node bin/index.mjs`; every index is regenerated, a data-only change. The README names the public scripts that check the graphs and regenerate the indexes.
- `scripts/bump-only.sh pr` removes its temporary directory on every exit; each `bump-only-pr` self-test case checks that its own `TMPDIR` is left empty (#28).
- `scripts/bump-only.sh` compares `fetched_at` as times, not strings, so `...:00.5Z` is later than `...:00Z` and `...:00.50Z` is not later than `...:00.5Z` (#26).
- `scripts/graphs.sh` lists a graph whose `check.json` names `graph/nodes/` with a trailing slash, so it is checked, auto-merge allowlisted and left without a CODEOWNERS owner like any other (#30).
- `scripts/render.sh [--check] [root]` takes a root as `scripts/index.sh` does; `selftest/render/` has a case for each of its guards, and `scripts/guards.py` a row for each (#25).
- The guards shard count is `guards.shards` in `policy/constants.json`, rendered into the job's matrix and its `--shard K/N`; `--shard` fails a shard that selects no row, and `selftest/guards-shard/` holds the hostile inputs (#103).

## v0.2.0

Checked against practice-library/.github v2.4.0 (`75a03317883e16f7ad93f1239dc53c9d0e1c4cc1`).

- Pins practice-library/.github v2.4.0 (#43), after v2.1.0 (#32). Through the shared node envelope, `vendors/schema.json` now also accepts `attrs.status` and the six legal-text edge relations; narrowing it again is #44. The required checks gain the four guard jobs: denylist, removed-paths, release-note and schema-loosening. The sources contract is checked against its upstream copy, with examples and counter-examples.
- `vendors/temporal`: Temporal Server releases with breaking flags and capabilities, and Temporal Cloud limits, plans, prices and included allocations; 65 nodes (#34).
- `.github/automerge-paths.json` keeps one path per line, so adding a graph adds only its own line (#38).
- README names the `guards` check and the new self-test categories (#31).

## v0.1.0

The first release: the contracts, checks and source policy, and the first two vendor graphs.
