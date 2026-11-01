#!/usr/bin/env bash
# Runs the cases under selftest/index/: each <case>/root/ is copied to a temporary directory, every
# _check.json renamed check.json (so discovery never takes a fixture for a real target), and
# scripts/index.sh --check runs on it; <case>/expect says pass (exit 0) or fail (any other exit).
# Usage: scripts/index-selftest.sh
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
failed=0
for c in "$root"/selftest/index/*/; do
  c="${c%/}"; name="selftest/index/$(basename "$c")"
  d="$(mktemp -d "$tmp/case.XXXXXX")"
  cp -R "$c/root/." "$d/"
  find "$d" -type f -name _check.json | while IFS= read -r f; do mv "$f" "$(dirname "$f")/check.json"; done
  rc=0; bash "$root/scripts/index.sh" --check "$d" >/dev/null 2>&1 || rc=$?
  case "$(cat "$c/expect"):$rc" in
    pass:0) echo "ok   $name passes" ;;
    fail:0) echo "FAIL $name: expected a failure, got success"; failed=1 ;;
    fail:*) echo "ok   $name fails (exit $rc)" ;;
    pass:*) echo "FAIL $name: expected success, got exit $rc"; failed=1 ;;
    *) echo "FAIL $name: expect must be pass or fail"; failed=1 ;;
  esac
done
exit "$failed"
