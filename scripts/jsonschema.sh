#!/usr/bin/env bash
# Runs the JSON Schema validator pinned in policy/constants.json (tools.jsonschema): the release zip for this
# platform is cached in ${JSONSCHEMA_CACHE:-$HOME/.cache/practice-graphs}, its sha256 is checked against the pin on
# every run (a mismatch fetches it again, and a fresh mismatch fails), it is unpacked into a new temporary directory,
# and every argument is passed to the validator. The same release and linux sha256 as the
# schema check of practice-library/.github.
#
# Usage: scripts/jsonschema.sh <validator arguments...>   e.g. scripts/jsonschema.sh validate <schema> <instance>
set -euo pipefail

die() { echo "$*" >&2; exit 1; }

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
constants="$here/../policy/constants.json"
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) platform=linux-x86_64 ;;
  Linux-aarch64 | Linux-arm64) platform=linux-arm64 ;;
  Darwin-arm64) platform=darwin-arm64 ;;
  Darwin-x86_64) platform=darwin-x86_64 ;;
  *) die "jsonschema.sh: no pinned validator for $(uname -s) $(uname -m)" ;;
esac
repo="$(jq -er '.tools.jsonschema.repo' "$constants")" || die "policy/constants.json has no tools.jsonschema.repo"
version="$(jq -er '.tools.jsonschema.version' "$constants")" || die "policy/constants.json has no tools.jsonschema.version"
sha="$(jq -er --arg p "$platform" '.tools.jsonschema.sha256[$p]' "$constants")" || die "policy/constants.json pins no jsonschema for $platform"
name="jsonschema-$version-$platform"
cache="${JSONSCHEMA_CACHE:-$HOME/.cache/practice-graphs}"
zip="$cache/$name.zip"

sha_of() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }

run="$(mktemp -d)"
trap 'rm -rf "$run"' EXIT
# Only the release zip is cached. Each run copies it into a new temporary directory and checks that copy against
# the pin, so the file checked is the file unpacked. A cached file that differs from the pin (tampered with,
# truncated, or left from an older pin) is never run: the zip is fetched again, and a fresh mismatch fails.
[ -f "$zip" ] && cp "$zip" "$run/archive.zip"
if [ ! -f "$run/archive.zip" ] || [ "$(sha_of "$run/archive.zip")" != "$sha" ]; then
  curl -fsSL --retry 3 "https://github.com/$repo/releases/download/v$version/$name.zip" -o "$run/archive.zip" \
    || die "jsonschema.sh: could not fetch $name.zip"
  got="$(sha_of "$run/archive.zip")"
  [ "$got" = "$sha" ] || die "jsonschema.sh: $name.zip has sha256 $got, not the pinned $sha"
  { mkdir -p "$cache" && cp "$run/archive.zip" "$zip.$$" && mv -f "$zip.$$" "$zip"; } 2>/dev/null || true
fi
unzip -q "$run/archive.zip" -d "$run" || die "jsonschema.sh: could not unpack $name.zip"
bin="$run/$name/bin/jsonschema"
[ -x "$bin" ] || die "jsonschema.sh: $name.zip holds no $name/bin/jsonschema"
"$bin" "$@"
