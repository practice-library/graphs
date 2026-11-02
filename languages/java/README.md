# languages/java

Facts about Java as the OpenJDK project publishes them: release versions and dates, release cadence, long-term support statements, the module system, the licence, and what the pages do not say about compatibility. One fact per file in `graph/nodes/`, listed in `INDEX.md`. The root node is `language.java`.

## Sources

All from `openjdk.org`:
- **Releases and dates:** the JDK Project page (`/projects/jdk/`) and each release's own page (`/projects/jdk/<n>/`, `/projects/jdk9/`).
- **Cadence and update lines:** the JDK Updates Project page (`/projects/jdk-updates/`).
- **Long-term support:** the pages of JDK 17, 21 and 25.
- **Toolchain and modules:** JEP 247 and JEP 261.
- **Licence:** `/legal/gplv2+ce.html` and the terms of use (`/legal/tou/`).
- **Compatibility:** the Compatibility & Specification Review group page (`/groups/csr/`).

**Host evidence:** `policy/sources.json` records that `openjdk.org/robots.txt` answers 404, so no path is disallowed. The terms of use (`/legal/tou/terms`, clause 5.a) bar robots, spiders and scrapers without express written permission, and exempt only crawling for a search index and read-only access for development of the code. That does not establish permission to refresh this graph automatically, so the scope in `policy/source-scopes.json` is `unresolved` and a refresh run reads nothing from this host until that is resolved.

## Not in this graph

- **Editions:** the pages read describe no edition or language level of Java, so there is no `edition` node.
- **A compatibility promise:** none is stated on the pages read. `compatibility-promise.java.source-compatibility` and `compatibility-promise.java.module-risk` are `unknown` with a note starting `Absent: `.
- **Calendar support periods:** the pages say a release is an LTS release "from most vendors" and give no end date, so an LTS window holds only the release's General Availability date, as its note says. Vendor support terms are not recorded.
- **JDK 8 and releases before 9:** not read.
- **Update-release cadence, the non-LTS maintenance tail and the Classpath Exception's grant:** not recorded yet. Their earlier quotes did not support the facts they were cited for, and the pages cannot be re-read automatically (see Host evidence).
- **A release in development:** the page for JDK 28 states no General Availability date in a quote that could be checked, and a release not yet shipped is not a node (`policy/graph-rules.json`, `languages.reachedWindowTypes`).

## The ten questions

1. **Which release is the latest, and when did it reach General Availability?** `release.java.27`: 2026-09-15.
2. **Which release came before the latest?** `release.java.26`, which `release.java.27` supersedes.
3. **How often does a feature release ship?** `version-line.java.feature-releases`: every six months.
4. **When does the first update of a series come?** `version-line.java.update-first-release`: within a month of the feature release's General Availability. The cadence of later update releases is not recorded yet.
5. **Which update lines are active?** `version-line.java.27-updates`, `.26-`, `.25-`, `.21-`, `.17-` and `.11-updates`; and which are retired: `version-line.java.retired-updates`.
6. **Which releases does the project page call LTS?** `support-window.java.lts-17`, `.lts-21` and `.lts-25`.
7. **How long are non-LTS releases maintained?** Not answered yet: no node records it.
8. **Which release introduced the module system, and what are its parts?** `module-system.java.jpms`, `.module-path` and `.unnamed-module`, each introduced in `release.java.9`.
9. **How does the compiler target an older release?** `toolchain.java.javac-release` (`javac --release`, from JDK 9).
10. **What is the licence, and does the project state a compatibility promise?** `licence.java.gplv2-ce` and `licence.java.default-outbound`; no promise is stated (`compatibility-promise.java.source-compatibility`).

## Attribution

The quoted passages are from openjdk.org and are short and unmodified. The ids, names, verdicts, windows and edges around them are this repository's own. Java and OpenJDK are trademarks of their owners and are named here only to refer to the software; the project does not endorse this repository.
