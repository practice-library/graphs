# vendors/temporal

Facts about Temporal Server and Temporal Cloud, one per file in `graph/nodes/`, listed in `INDEX.md`.

This is a versioned graph:
- `product.temporal.server` links to its releases (`hasRelease`).
- A capability points at the release that introduced or removed it (`introducedIn`, `removedIn`).
- A release names its version in `attrs.scope` and its publication date in `attrs.window`.
- A release flagged breaking has a `note` starting with "Breaking".
- A fact the sources do not state is kept as `unknown` with a note starting "Absent: ".

Cloud limits, plans and prices hang off `product.temporal.cloud`. Self-hosted defaults hang off `product.temporal.server`.

## Sources

- **Release notes:** read from the public releases endpoint of the temporalio/temporal repository on api.github.com, one URL per release tag, as raw JSON text.
  - `attrs.quote` is a run of characters from that text, within one line of the notes.
  - Quotes avoid the start of a line, because in JSON text a line break is the escape `\n`, which joins the line's first word to the letter `n`.
- **Documentation:** read from docs.temporal.io, as the page's visible text.
- `attrs.fetched_at` is the time each page was read.
- Each host's robots.txt and terms are recorded in `policy/sources.json`.

## Attribution and terms

- **Documentation:** the quoted text is from the Temporal documentation (https://docs.temporal.io), whose source repository, temporalio/documentation, is under the MIT License (https://github.com/temporalio/documentation/blob/main/LICENSE.md). Copyright Temporal Technologies Inc. and Uber Technologies, Inc.
- **Release notes:** these are published by Temporal on GitHub and are not files of the temporalio/temporal repository. This repository does not assume that repository's licence covers them.
- Only short quotes are kept, without change, and no page is copied in bulk.
- The ids, names, verdicts, values and edges around the quotes are this repository's own, and Temporal does not endorse them.
