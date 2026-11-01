# vendors/gitleaks

Facts about gitleaks, the open-source secret scanner (MIT), one per file in `graph/nodes/`, listed in `INDEX.md`. The acceptance questions are in #49.

## Sources

- **README and licence:** the README and LICENSE files of the gitleaks/gitleaks repository, read as plain text from raw.githubusercontent.com.
- **Releases:** from api.github.com, as raw JSON text: the releases list (the 30 most recent) and the latest release's tag.
- **Host evidence:** each host's robots.txt and terms are recorded in `policy/sources.json`.

## The ten questions

1. **Licence:** `term.gitleaks.licence`.
2. **Latest release:** `release.gitleaks.gitleaks.8-30-1`.
3. **Releases flagged breaking:** `rule.gitleaks.breaking-releases` is absent. None of the 30 most recent releases flags one.
4. **Config format and keys:** `feature.gitleaks.config.rules`, `.config.entropy` and `.config.keywords`.
5. **Extending the defaults:** `feature.gitleaks.config.extend`.
6. **Scan modes:** `feature.gitleaks.command.git`, `.command.dir` and `.command.stdin`, and `rule.gitleaks.detect-protect-deprecated`.
7. **Exit code:** `rule.gitleaks.exit-code-leaks`.
8. **Report formats:** `feature.gitleaks.command.report-formats`.
9. **Ignoring findings:** `feature.gitleaks.ignore.inline`, `.ignore.gitleaksignore` and `.config.allowlists`.
10. **Scanning limits:** `limit.gitleaks.max-target-megabytes`, `.max-archive-depth` and `.max-decode-depth`.

## Attribution

The quoted text is from the gitleaks README, LICENSE and release notes on GitHub. The repository is under the MIT License (https://github.com/gitleaks/gitleaks/blob/master/LICENSE). Quotes are short and unmodified. The ids, names, verdicts, values and edges around them are this repository's own, and the gitleaks project does not endorse them.
