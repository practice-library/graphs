# practice-library/.github v2.6.0

Files copied unchanged from https://github.com/practice-library/.github at tag v2.6.0 (commit 1927f933ff655934a99660161efc0ca277eea8f0), so a check here can resolve them by `$id`:

- `spec/sources/schema.json`: `https://github.com/practice-library/.github/spec/sources/schema.json`, which `policy/check.json` names in `resolve` and `resolve-ids`.

When the pinned release moves, copy the new files under a directory named for the new tag, and remove this one in the same pull request. The `schema-loosening` guard counts a removed schema as loosened, so that pull request needs the `schema-loosening-approved` label from a maintainer who is not its author; the reviewer should confirm that the new copy is the file at the new tag and that `policy/check.json` names it, before the label is added.
