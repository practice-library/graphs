# Contracts

Each contract is a directory with `schema.json` (JSON Schema 2020-12), `examples/` that must pass and `counter-examples/` that must fail, each for one named reason. `scripts/discover.sh` lists them all, including the node schema of every domain, for the organisation's schema check: the examples with expect pass, each counter-example on its own with expect fail. Code that reads or writes these files is generated from, or tested against, these schemas.

## refresh-report

The seam between public CI and the maintainer's machine.

### The refresh run (planned: the workflow does not exist yet)

It will run in public CI with no secret and push nothing. Until it exists, these are the rules it is built and tested against.

1. **robots.txt first, every run.** Before fetching any page, the run fetches robots.txt of every host it would read and records each in `robots`. When one disallows a path the run would fetch, or cannot be read (5xx or network error, which counts as a disallow), the run fetches no page and records `aborted`; a 4xx means no robots.txt, recorded as `absent`.
2. **Only listed hosts.** Pages come only from hosts in `policy/sources.json`, redirects included, within each host's `maxRequestsPerRun`, `maxBytes` and `timeoutSeconds`, with the listed user agent and conditional requests.
3. **A run-wide cap.** `maxRequestsPerRun` in `policy/sources.json` bounds the whole run, robots.txt included; `requests` records the count. When the cap is reached the run stops; facts not reached wait for the next run, which starts from the oldest `measuredAt`.
4. **429 and 503.** With `Retry-After` at most `retryAfterMaxSeconds`, the run waits and retries once; otherwise, or when the retry fails too, it stops fetching that host for the run, and that host's remaining facts are `unreadable` with the status and `retryAfterSeconds` recorded. It never retries a page twice.
5. **The report.** For each fact fetched: `unchanged` when its quote is in the page text, `changed` when the page was read and the quote is not in it, `unreadable` otherwise, with the reason.

### The PR opener (planned: the maintainer's machine, the organisation's app)

It downloads the report, validates it against this schema and refuses one whose commit is not on main. Then:

- `unchanged`: one pull request bumping `measuredAt` and `attrs.fetched_at` of those facts and nothing else. Only such a pull request can pass the `bump-only` check while touching allowlisted paths alone, so only it may auto-merge.
- `changed`: one pull request per fact that records the finding in the vendor's `CHANGES.md` and does not touch the node. That path is outside the allowlist, so it waits for a maintainer; the corrected node is pushed to the same branch.
- `unreadable`: no pull request. When the same fact is `unreadable` in the last `unreadableRunsBeforeIssue` reports, the opener opens one issue labelled `unreadable-source` for it, or comments on the one already open.
- `aborted`: no pull request; the opener opens or updates one issue labelled `robots` naming the host and the reason.

### Merges by GITHUB_TOKEN start no push run on main

`automerge.yml` turns auto-merge on with the workflow's `GITHUB_TOKEN`, so GitHub merges the pull request as `github-actions`. Events caused by `GITHUB_TOKEN` start no new workflow run (except `workflow_dispatch` and `repository_dispatch`), so an auto-merged date bump starts no `push` run of `checks.yml` on main. Such a merge is checked only by the pull request's own run; a pull request merged by a person does start the push run.

## sources

`policy/sources.json` (it lists no host yet): the run-wide request cap, the Retry-After limit and how many unreadable runs open an issue; then every host a node may cite, with its robots.txt verdict when it was added, the sentence of its terms that bears on automated reading, the page format and the per-host limits. The robots.txt verdict here is evidence for adding the host; the run still re-reads robots.txt every time. Adding a host is a pull request that carries that evidence. A host whose robots.txt disallows us is not listed.

## Issue forms

`.github/ISSUE_TEMPLATE/fact-request.yml` asks for a new fact: the graph, the question, and optionally the source and quote. GitHub validates the form when it renders it; nothing runs on a new issue. The graph is free text, so adding a vendor never edits the form.
