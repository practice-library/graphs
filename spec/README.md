# Contracts

The `sources` contract lives only in practice-library/.github, pinned under `policy/upstream/`, with the `$id` `https://github.com/practice-library/.github/spec/sources/schema.json`; this directory keeps its `examples/` and `counter-examples/`, and `policy/check.json` validates them, and `policy/sources.json`, against the pinned schema, so there is one contract to read. The `refresh-report` schema stays here until the .github release that carries the rules below.

Each contract is a directory with `schema.json` (JSON Schema 2020-12), `examples/` that must pass and `counter-examples/` that must fail, each for one named reason. Its `check.json` lists two targets for the organisation's schema check: the examples with expect pass, and the counter-examples with expect fail and `each`, so every one of them must fail on its own. The node schema of every domain is checked the same way. Code that reads or writes these files is generated from, or tested against, these schemas.

## refresh-report

The seam between public CI and the maintainer's machine.

### The refresh run (planned: the workflow does not exist yet)

It will run in public CI with no secret and push nothing. Until it exists, these are the rules it is built and tested against.

1. **robots.txt first, every run.** Before fetching any page, the run fetches robots.txt of every host it would read and records each in `robots` (never empty) with the status it got. Only a 404 or 410 is `absent`: no robots.txt, no rule. A 2xx that permits the paths is `allowed`. Everything else stops the run, which fetches no page and records `aborted`: `disallowed` (a rule forbids a path), `refused` (401, 403 or any other 4xx but 404, 410 and 429, an explicit refusal, never read as absent), `throttled` (429), `challenge` (a bot-challenge page instead of robots.txt) and `unreachable` (5xx or a network error). A host that refuses is not retried until something changes; `policy/blocked-hosts.md` records it.
2. **Only approved hosts, paths and repositories.** Pages come only from hosts in `policy/sources.json`, redirects included, within each host's `maxRequestsPerRun`, `maxBytes` and `timeoutSeconds`, with the listed user agent and conditional requests. `policy/source-scopes.json` narrows each entry to the paths (a repository on a shared host is a path prefix) its evidence covers and names the paths robots.txt disallows; `scripts/sources-check.py` fails a node that cites outside them. A host whose scope says `permission.state: unresolved` (its terms were read, and no clause shows that automated reading is permitted) is read from by nobody: the run fetches nothing from it until a pull request records the clause that governs, and its licence, and sets the state to `established`.
3. **A run-wide cap.** `maxRequestsPerRun` in `policy/sources.json` bounds the whole run, robots.txt included; `requests` records the count and `fetches` lists every request in order with its status, the bytes read and the redirect path. The fetcher counts bytes while streaming and stops at the host's `maxBytes`. When the cap is reached the run stops; facts not reached wait for the next run, which starts from the oldest `measuredAt`. `scripts/report-check.py check` holds a report to the exact policy and commit: the count, robots.txt first and from the host itself, every hop on a listed host, each host within its request cap and each response within its size cap.
4. **429 and 503.** With `Retry-After` at most `retryAfterMaxSeconds`, the run waits and retries once; otherwise, or when the retry fails too, it stops fetching that host for the run, and that host's remaining facts are `unreadable` with the status and `retryAfterSeconds` recorded. It never retries a page twice.
5. **The report.** For each fact fetched: `unchanged` when its quote is in the page text, `changed` when the page was read and the quote is not in it, `unreadable` otherwise, with the reason.
6. **What a quote must cover, and what it cannot.** A node's quote states its asserted value, its subject and its qualification (`scripts/quote-value.py` checks the number). A fragment found on a page shows only that the fragment is there. A claim that something is the latest, that nothing newer or nothing else exists, or that a figure is a count over a set, is a `latest`, `absence` or `aggregate` claim: it is refreshed by a query over the whole relevant set (the releases list sorted and filtered, the table counted), recorded in the result's `query` with how many members were read, and is never `unchanged` because a fragment is still in the list.

### The PR opener (planned: the maintainer's machine, the organisation's app)

It downloads the report, validates it against this schema and refuses one whose commit is not on main. Then:

- `unchanged`: one pull request bumping `measuredAt` and `attrs.fetched_at` of those facts and nothing else, and adding the report that supports it as `<graph>/graph/refresh/<run id>.json`. Only such a pull request can pass the `bump-only` check while touching allowlisted paths alone, so only it may auto-merge. `bump-only` verifies the binding: the report passes `scripts/report-check.py` under the base commit's policy, names a commit that is an ancestor of the base with the node unchanged since, and holds an `unchanged` result for each bumped node, for the source the node cites, fetched exactly at the node's new `fetched_at`. A bump with no report, or an edited date with no fetch behind it, fails. Each graph's `INDEX.md` leaves `measuredAt` and `fetched_at` out, so a bump regenerates nothing.
- `changed`: one pull request per fact that records the finding in the vendor's `CHANGES.md` and does not touch the node. That path is outside the allowlist, so it waits for a maintainer; the corrected node is pushed to the same branch.
- `unreadable`: no pull request. When the same fact is `unreadable` in the last `unreadableRunsBeforeIssue` reports, the opener opens one issue labelled `unreadable-source` for it, or comments on the one already open.
- `aborted`: no pull request; the opener opens or updates one issue labelled `robots` naming the host and the reason.

### Merges by GITHUB_TOKEN start no push run on main

`automerge.yml` turns auto-merge on with the workflow's `GITHUB_TOKEN`, so GitHub merges the pull request as `github-actions`. Events caused by `GITHUB_TOKEN` start no new workflow run (except `workflow_dispatch` and `repository_dispatch`), so an auto-merged date bump starts no `push` run of `checks.yml` on main. Such a merge is checked only by the pull request's own run; a pull request merged by a person does start the push run.

## sources

`policy/sources.json`: the run-wide request cap, the Retry-After limit and how many unreadable runs open an issue; then every host a node may cite, with its robots.txt verdict when it was added, the sentence of its terms that bears on automated reading, the page format and the per-host limits. The robots.txt verdict here is evidence for adding the host; the run still re-reads robots.txt every time. Adding a host is a pull request that carries that evidence. A host whose robots.txt disallows or refuses us is not listed. Each graph and host is listed once, and an entry's robots url is `/robots.txt` of its own host.

`policy/source-scopes.json` (beside it, because the pinned contract allows no extra field) holds one scope per entry: the path prefixes it covers, the prefixes robots.txt disallows, and the permission: `established` with the clause that governs automated reading or reproduction and the page it is on, or `unresolved` with the reason (a liability disclaimer, the introduction of the terms, a definition of scraping, or the host's general terms for documentation whose own licence is not recorded). Moving these fields into the contract is for the .github release that follows the pin.

## Issue forms

`.github/ISSUE_TEMPLATE/fact-request.yml` asks for a new fact: the graph, the question, and optionally the source and quote. GitHub validates the form when it renders it; nothing runs on a new issue. The graph is free text, so adding a vendor never edits the form.
