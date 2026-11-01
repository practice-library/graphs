# vendors/postgresql

Facts about PostgreSQL, the open-source database: its licence, supported versions and release schedule, documented limits, upgrades, security process and trademark policy. One fact per file in `graph/nodes/`, listed in `INDEX.md`. The acceptance questions are in #62.

A managed PostgreSQL service with a free tier is a separate graph (#36 step 6).

## Sources

All from `www.postgresql.org`:
- **Licence:** the licence page.
- **Versions and support:** the versioning policy, with its table of current minor, first release and final release per major version.
- **Schedule:** the developer roadmap, for upcoming minor release dates.
- **Latest minor release date:** the release notes of 18.6.
- **Limits and upgrades:** the current documentation: Appendix K, PostgreSQL Limits, and Upgrading a PostgreSQL Cluster.
- **Security:** the security page: reporting, and known vulnerabilities in supported versions.
- **Name:** the trademark policy.

**Host evidence:** robots.txt and the licence are recorded in `policy/sources.json`. robots.txt disallows `/docs/devel/` and some account, list and search paths, and none of them is cited. The licence covers "this software and its documentation".

## The ten questions

1. **Licence:** `term.postgresql.licence` and `rule.postgresql.licence-notice`.
2. **Supported versions:** `release.postgresql.server.18`, `.17`, `.16`, `.15` and `.14`, with their final releases in each note, and `rule.postgresql.unsupported-13`.
3. **Support window:** `rule.postgresql.support-window` (five years).
4. **Current releases:** the current minor in each release node's scope, released on the date in `release.postgresql.server.minor-2026-08-13`.
5. **Release cadence:** `rule.postgresql.minor-release-schedule`, with the next scheduled dates in its note.
6. **Size limits:** `limit.postgresql.server.database-size`, `.relation-size`, `.row-size`, `.field-size` and `.rows-per-table`.
7. **Schema limits:** `limit.postgresql.server.columns-per-table`, `.columns-per-index` and `.identifier-length`.
8. **Upgrades:** `rule.postgresql.minor-upgrade`, `rule.postgresql.major-upgrade` and `rule.postgresql.storage-format`.
9. **Security:** `rule.postgresql.security-reporting` and `rule.postgresql.latest-security-fixes`.
10. **Name:** `term.postgresql.trademark` and `permission.postgresql.trademark-fair-use`.

## Dates to watch

- **PostgreSQL 14:** final release on 2026-11-12, after which it is unsupported. A refresh after that date must move it out of the supported set.
- **Next minor release:** the next scheduled minor release is also on 2026-11-12, so the current minor versions change then too.
- **PostgreSQL 19:** the roadmap plans it for October 2026, and on 2026-11-01 it is at its first release candidate. It is not in this graph until it is released.

## Attribution

The quoted passages are from www.postgresql.org. The software and its documentation are under the PostgreSQL License. Quotes are short and unmodified. The ids, names, verdicts, values and edges around them are this repository's own. PostgreSQL and Postgres are registered trademarks of the PostgreSQL Community Association of Canada. They are named here only to refer to the software, and the project does not endorse this repository.
