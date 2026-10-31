#!/usr/bin/env bash
# Runs every self-test case. A case is a directory under selftest/<script>/ holding `expect`
# (pass or fail) and its inputs; the case passes when the script's exit status matches:
# 0 for pass, anything but 0 for fail.
#   selftest/discover/<case>/root/        scripts/discover.sh <root>
# Usage: scripts/selftest.sh
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

failed=0
count=0
run_case() { # <case dir> <command...>
  local dir="$1"; shift
  local expect rc=0
  expect="$(cat "$dir/expect")"
  "$@" >/dev/null 2>&1 || rc=$?
  count=$((count + 1))
  case "$expect:$rc" in
    pass:0) echo "ok   $dir passes" ;;
    fail:0) echo "FAIL $dir: expected a failure, got success"; failed=1 ;;
    fail:*) echo "ok   $dir fails (exit $rc)" ;;
    pass:*) echo "FAIL $dir: expected success, got exit $rc"; failed=1 ;;
    *) echo "FAIL $dir: expect must be pass or fail"; failed=1 ;;
  esac
}

for c in selftest/discover/*/; do run_case "${c%/}" bash scripts/discover.sh "${c}root"; done

[ "$count" -gt 0 ] || { echo "no self-test case found"; exit 1; }
echo "$count cases"
exit "$failed"
