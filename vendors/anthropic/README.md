# vendors/anthropic

Facts about Anthropic's Claude API and Claude Code, one per file in `graph/nodes/`, listed in `INDEX.md`. This is the first versioned graph: each product links to its releases (`hasRelease`), and a capability points at the release that introduced or removed it (`introducedIn`, `removedIn`). A release names its version or model id in `attrs.scope` and, when the page states it, its date in `attrs.window`. A release flagged breaking has a `note` starting with "Breaking".

## Attribution and terms

Each fact quotes Anthropic's public documentation and names the page it was read from: `source` is that page's URL on platform.claude.com or code.claude.com, and `attrs.quote` is a short passage copied from it without change, with `attrs.fetched_at` the time it was read. Only short quotes are kept; no page is copied in bulk.

The quoted text is Anthropic's and stays under Anthropic's terms (https://www.anthropic.com/legal/consumer-terms), which this repository has not been granted any other licence to. Each host's robots.txt is honoured and recorded in `policy/sources.json`, and a host that blocks fetching is not read. The ids, names, verdicts, values and edges around the quotes are this repository's own, and Anthropic does not endorse them.
