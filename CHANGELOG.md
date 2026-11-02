# Changelog

One entry per release of this repository. A release names the practice-library/.github release its own CI checked it against.

## Unreleased

- Pins practice-library/.github v3.0.0 (`f49b1a054c45a99b5874ff4ef34f77269c621b72`), after v2.6.0. Every reusable workflow call in `.github/workflows/` moves to that commit, rendered from `policy/constants.json`.
- The guards check out their own tooling at the pinned commit. A loosened schema, or a denylist exemption that is added or widened, now needs a maintainer's approval of the pull request's exact head; the `schema-loosening-approved` label only re-runs the check.
- The pinned sources contract moves to `policy/upstream/practice-library-.github/v3.0.0/`, an unchanged copy of the file at that commit, and `policy/check.json` resolves it there. At v3.0.0 a host's `terms` may carry an optional `note` (at most 300 characters) for terms with no clause on automated reading.
- No caller input, check name or required job changes: the v3.0.0 caller keeps the same inputs, and this repository used none of the removed paths, inputs or constants.
- Known: regulation nodes with the status `expired`, `repealed` or `never-effective` fail the schema check until the shared envelope adds those values (practice-library/.github v3.1.0).

## v0.2.0

Checked against practice-library/.github v2.4.0 (`75a03317883e16f7ad93f1239dc53c9d0e1c4cc1`).

- Pins practice-library/.github v2.4.0 (#43), after v2.1.0 (#32). Through the shared node envelope, `vendors/schema.json` now also accepts `attrs.status` and the six legal-text edge relations; narrowing it again is #44. The required checks gain the four guard jobs: denylist, removed-paths, release-note and schema-loosening. The sources contract is checked against its upstream copy, with examples and counter-examples.
- `vendors/temporal`: Temporal Server releases with breaking flags and capabilities, and Temporal Cloud limits, plans, prices and included allocations; 65 nodes (#34).
- `.github/automerge-paths.json` keeps one path per line, so adding a graph adds only its own line (#38).
- README names the `guards` check and the new self-test categories (#31).

## v0.1.0

The first release: the contracts, checks and source policy, and the first two vendor graphs.
