# languages/rust

Facts about the Rust programming language: its release lines and versions, release cadence, which release is supported, its compatibility promises, editions, toolchain, module and package system, and licence. One fact per file in `graph/nodes/`, listed in `INDEX.md`. The root node is `language.rust`.

## Sources

All from hosts of the Rust project, listed for `rust` in `policy/sources.json`:
- **`www.rust-lang.org`:** the home page (the one-line description), the licences page, the security policy (which release is supported) and the install page (rustup and the toolchain).
- **`blog.rust-lang.org`:** one announcement per release in the graph: Rust 1.0, the releases that introduced an edition (1.31.0, 1.56.0, 1.85.0) and every release from 1.92.0 to 1.99.1, each with its date from the post's URL.
- **`doc.rust-lang.org`:** under `/stable/` only: the Book (release channels, the module system, crates and packages, publishing), the Edition Guide, the Cargo book (manifest, `rust-version`) and the rustc book (platform tiers).
- **`forge.rust-lang.org`:** the release process page.

**Host evidence:** robots.txt and the licence are recorded in `policy/sources.json` and `policy/source-scopes.json`. `www.rust-lang.org` and `forge.rust-lang.org` have no robots.txt (404). `blog.rust-lang.org` allows everything. `doc.rust-lang.org` disallows `/0.` and `/1.` (versioned documentation) and the first and second edition books; no node cites those, and the scope for the host is `/stable/` with the book paths listed as disallowed. The licences page says the project and "all other official projects" are generally dual-licensed (Apache-2.0 and MIT), which is the permission recorded for every host; the word "generally" is the page's own.

## Modelling notes

- A release's `window` is its release date. A point release supersedes the release it fixes, and each minor release supersedes the previous release in the chain.
- The release cadence has no node type of its own: it is on `version-line.rust.1` (quote and note), with the release train, the release channels and the release day as `toolchain` nodes.
- `support-window.rust.latest-stable` records the policy that only the most recent stable release is supported. The page names no version or date, so its window starts on the release date of the release it supports on `measuredAt`.
- Editions are `introducedIn` the release that stabilised them, per the Edition Guide or the release post.
- Platform tiers are `toolchain` nodes: they describe what the compiler's targets are guaranteed to do.
- Quotes are exact substrings of the page's text with markup removed.

## The ten questions

1. **What is Rust?** `language.rust`.
2. **Which is the latest release and when was it published?** `release.rust.1-99-1` (2026-10-15), which supersedes `release.rust.1-99-0` (2026-10-01); the chain back to `release.rust.1-92-0` gives the earlier dates.
3. **How often does Rust release?** `version-line.rust.1` (every six weeks), `toolchain.rust.release-train`, and `toolchain.rust.release-process` (release day is a Thursday, within one UTC day).
4. **Which release is supported?** `support-window.rust.latest-stable`: only the most recent stable release gets support and security updates; its `appliesTo` edge points at `release.rust.1-99-1`.
5. **What is the compatibility promise?** `compatibility-promise.rust.stability-without-stagnation`, `compatibility-promise.rust.commitment-from-1-0`, and for breaking changes `compatibility-promise.rust.edition-breaking-changes`.
6. **Which editions exist and which release introduced each?** `edition.rust.2015` (`release.rust.1-0-0`), `.2018` (`release.rust.1-31-0`), `.2021` (`release.rust.1-56-0`) and `.2024` (`release.rust.1-85-0`).
7. **Which edition applies by default?** `edition.rust.2015` when the manifest has none, and `toolchain.rust.cargo-edition-field` (`cargo new` writes the 2024 edition).
8. **How do crates of different editions work together, and how does a crate move to a new edition?** `compatibility-promise.rust.edition-interop`, `compatibility-promise.rust.edition-migration-independent` and `toolchain.rust.edition-migration`.
9. **What is the toolchain and how are packages organised?** `toolchain.rust.rustup`, `toolchain.rust.install-bundle`, `toolchain.rust.cargo`, `module-system.rust.overview`, `.crates`, `.packages`, `.package-contents`, `.manifest`, `.workspaces` and `.crates-io`; the minimum Rust version of a package is `toolchain.rust.cargo-rust-version`.
10. **Under which licence is Rust available?** `licence.rust.dual` (MIT OR Apache-2.0).

## Attribution

The quoted passages are from the Rust project's own sites, which it releases under the licences named in `licence.rust.dual`. Quotes are short and unmodified. The ids, names, verdicts, windows and edges around them are this repository's own. Rust is named here only to refer to the language; the Rust project does not endorse this repository.
