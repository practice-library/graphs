# practice-library/.github v3.0.0

Files copied unchanged from https://github.com/practice-library/.github at tag v3.0.0 (commit f49b1a054c45a99b5874ff4ef34f77269c621b72), so a check here can resolve them by `$id`:

- `spec/sources/schema.json`: `https://github.com/practice-library/.github/spec/sources/schema.json`, which `policy/check.json` names in `resolve` and `resolve-ids`.

When the pinned release moves, copy the new files under a directory named for the new tag, and remove this one in the same pull request. The `schema-loosening` guard reads a moved file as a rename and compares the old copy with the new one, so a copy that is unchanged at the new tag passes without a label. If the file changed between the tags, the guard judges that change, and a loosening needs a maintainer who is not the author to approve the pull request's exact head (since v3.0.0 an approval counts only for the commit it was given on, and the `schema-loosening-approved` label only re-runs the check). Either way, the reviewer confirms that the new copy is the file at the new tag and that `policy/check.json` names it.
