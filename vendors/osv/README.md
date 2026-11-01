# vendors/osv

Facts about OSV (Open Source Vulnerabilities): the OSV.dev database and API, the OSV schema, and OSV-Scanner. One fact per file in `graph/nodes/`, listed in `INDEX.md`. The acceptance questions are in #49.

## Sources

- **OSV.dev:** its home page.
- **Documentation:** google.github.io/osv.dev (data sources, contributing data, FAQ and the API pages) and the OSV-Scanner page on supported lockfiles.
- **Schema:** the OSV schema specification at ossf.github.io/osv-schema.
- **Licences:** the LICENSE files of google/osv.dev and google/osv-scanner, from raw.githubusercontent.com.
- **OSV-Scanner releases:** from api.github.com, as raw JSON text.
- **Host evidence:** each host's robots.txt and terms are recorded in `policy/sources.json`.

## The ten questions

1. **Code licences:** `term.osv.licence.osv-dev` and `term.osv.licence.osv-scanner`.
2. **Data terms:** `term.osv.data-licensing`, plus four per-source examples, `term.osv.data-licence.*`. They include a CC-BY-SA source and a non-commercial CC-BY-NC-ND source.
3. **Ecosystems:** `feature.osv.covered-ecosystems`.
4. **Schema version and required fields:** `release.osv.schema.1-9-2` and `rule.osv.schema.required-fields`.
5. **API endpoints:** `feature.osv.api.query`, `.querybatch` and `.vulns`.
6. **Limits:**
   - `rate-limit.osv.api`: none;
   - `limit.osv.api.response-size`: 32 MiB over HTTP/1.1;
   - `limit.osv.api.query-page-size`: 1,000 vulnerabilities per page of `/v1/query`;
   - `limit.osv.api.querybatch-page-size`: 3,000 vulnerabilities per page of a whole `/v1/querybatch` (1,000 for one query in it);
   - `limit.osv.api.querybatch-size`: absent.
7. **Authentication:** `permission.osv.api.authentication` is absent. The pages checked mention no key.
8. **Bulk download:** `feature.osv.bulk.all-zip`.
9. **OSV-Scanner releases:** `release.osv.osv-scanner.2-7-0` (latest) and `release.osv.osv-scanner.2-0-0` (breaking). `rule.osv.osv-scanner.breaking-releases` covers the 30 most recent releases.
10. **Lockfiles:** `feature.osv.osv-scanner.lockfiles`.

## Attribution

The quoted text is from the OSV.dev documentation and site, the OSV schema specification, and the OSV-Scanner documentation and release notes. The OSV.dev and OSV-Scanner repositories are under the Apache License 2.0. Vulnerability records themselves keep the licence of their data source, which the data page lists per source. Quotes are short and unmodified. The ids, names, verdicts, values and edges around them are this repository's own, and the OSV project does not endorse them.
