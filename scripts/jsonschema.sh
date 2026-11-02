#!/usr/bin/env bash
# Runs the JSON Schema validator pinned in policy/constants.json (tools.jsonschema): the release zip for this
# platform is fetched once into ${JSONSCHEMA_CACHE:-$HOME/.cache/practice-graphs}, its sha256 checked against the
# pin before it is unpacked, and every argument passed to the validator. The same release and linux sha256 as the
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
dir="${JSONSCHEMA_CACHE:-$HOME/.cache/practice-graphs}/$name"
bin="$dir/$name/bin/jsonschema"

if [ ! -x "$bin" ]; then
  mkdir -p "$dir"
  tmp="$(mktemp "$dir/archive.XXXXXX")"
  trap 'rm -f "$tmp"' EXIT
  curl -fsSL --retry 3 "https://github.com/$repo/releases/download/v$version/$name.zip" -o "$tmp" \
    || die "jsonschema.sh: could not fetch $name.zip"
  if command -v sha256sum >/dev/null; then got="$(sha256sum "$tmp")"; else got="$(shasum -a 256 "$tmp")"; fi
  [ "${got%% *}" = "$sha" ] || die "jsonschema.sh: $name.zip has sha256 ${got%% *}, not the pinned $sha"
  unzip -q -o "$tmp" -d "$dir"
  [ -x "$bin" ] || die "jsonschema.sh: $name.zip holds no $name/bin/jsonschema"
fi
exec "$bin" "$@"
