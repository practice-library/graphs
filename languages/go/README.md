# languages/go

Facts about the Go programming language, read from `go.dev`: release lines and versions, the release cadence, the support rule, the Go 1 compatibility promise, the language version, the module and toolchain system, and the licence. One fact per file in `graph/nodes/`, listed in `INDEX.md`. The root is `language.go`.

Node types follow `languages/schema.json`: `release` (version in `attrs.scope`, date in `attrs.window`), `version-line`, `support-window`, `compatibility-promise`, `module-system`, `toolchain`, `edition` and `licence` (SPDX identifier in `attrs.scope`). A `version-line` node is also used for the release cadence, because the schema has no cadence type.

## Sources

All from `go.dev`, one host:
- **Releases and support:** the release history (`/doc/devel/release`), with its release policy and each major and minor release date; the release cycle page (`/wiki/Go-Release-Cycle`); the Go 1.27 release notes.
- **Compatibility:** the Go 1 and the Go toolchain compatibility document (`/doc/go1compat`) and the GODEBUG page (`/doc/godebug`).
- **Toolchain and modules:** `/doc/toolchain`, `/ref/mod` and `/doc/install`.
- **Licence:** `/copyright` and `/LICENSE`.

**Host evidence:** `policy/sources.json` records robots.txt (`User-agent: *`, `Allow: /`, nothing disallowed) and the licence statement of `/copyright`; `policy/source-scopes.json` records the permission clause. Quotes were read through a page-to-text fetcher that converts markup; they drop link markup and code formatting, and the next refresh must re-confirm each against the page text.

## What the graph does not state

- **Go 1.25:** the release policy says a major release is supported until there are two newer major releases, but the page gives no status or end date for Go 1.25, so `support-window.go.1-25` is `unknown` with that reason.
- **Editions:** `edition.go.editions` is an absent fact: the pages checked describe no edition mechanism. The nearest statement, the language version `1.N`, is `edition.go.language-version`.
- **LTS:** no page read states a long-term-support line, so there is no node for one.

## The ten questions

1. **Newest major release:** `release.go.1-27-0` (2026-08-19), in `version-line.go.1-27`, which supersedes `version-line.go.1-26`.
2. **Cadence:** `version-line.go.cadence` (every six months), `version-line.go.cadence-months` (August and February) and `version-line.go.1-27-arrival`.
3. **Support rule:** `support-window.go.1-27` and `support-window.go.1-26`: a major release is supported until there are two newer major releases.
4. **Fixes in supported releases:** `support-window.go.minor-revisions` and `support-window.go.1-26-minor-stop`.
5. **Latest minor revisions listed:** `release.go.1-27-3` and `release.go.1-26-10`, both 2026-10-19, with `release.go.1-25-14` the last go1.25 revision; `support-window.go.1-25` says what is not stated.
6. **The Go 1 promise:** `compatibility-promise.go.source`, `.binary`, `.recompile` and `.api-growth`.
7. **What it does not cover:** `compatibility-promise.go.security`, `.unspecified`, `.bugs`, `.struct-literals`, `.unsafe`, `.syscall`, `.subrepositories` and `.tools`.
8. **Opting back in to old behaviour:** `compatibility-promise.go.godebug-optin`, `.godebug-retention` (two years, four releases) and `.go-line-defaults`.
9. **Modules and toolchain:** `module-system.go.modules`, `.go-mod`, `.module-path`, `.major-suffix`, `.mvs` and `.proxy`; `toolchain.go.go-line`, `.toolchain-line`, `.go-line-mandatory`, `.gotoolchain`, `.version-syntax` and `.version-order`; and the language level in `edition.go.language-version`, with `edition.go.editions` for what is absent.
10. **Licence:** `licence.go.code` (BSD), `licence.go.site-content` (CC-BY-4.0), `licence.go.redistribution` and `licence.go.no-endorsement`.

## Dates to watch

- **Go 1.28:** the cadence puts the next major release in February 2027. It is not in this graph until it is released; a refresh then must re-read the support nodes.
- **Minor revisions:** each new minor revision of go1.27 and go1.26 changes the latest-release nodes.

## Attribution

The quoted passages are from go.dev. The site contents are under the Creative Commons Attribution 4.0 License and the code under a BSD licence, as quoted in the licence nodes. Quotes are short and kept as read. The ids, names, verdicts, scopes, windows and edges around them are this repository's own, and the project does not endorse this repository.
