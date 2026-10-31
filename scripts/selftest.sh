#!/usr/bin/env bash
# Runs every self-test case. A case is a directory under selftest/<script>/ holding `expect`
# (pass or fail) and its inputs; the case passes when the script's exit status matches:
# 0 for pass, anything but 0 for fail.
# A case's root/ keeps each check.json as _check.json, so the organisation's discover workflow,
# which finds every tracked check.json, never takes a fixture for a real target. Each root is
# copied to a temporary directory with those files renamed before the script runs on it.
#   selftest/graph-check/<case>/root/                     scripts/graph-check.sh <root>
#   selftest/bump-only-file/<case>/{old,new}.json          scripts/bump-only.sh file <old> <new>
# Other cases compare the script's output with `expect` instead:
#   selftest/bump-only-classify/<case>/{allow.json,diff}   scripts/bump-only.sh classify (review, bump or reject)
#   selftest/graphs/<case>/root/                           scripts/graphs.sh <root>
# and these run scripts/bump-only.sh where it must fail or run against a commit:
#   selftest/bump-only-classify-fails/<case>/{allow.json,diff}  scripts/bump-only.sh classify (expect fail)
#   selftest/bump-only-pr/<case>/{base,head}/[event]       scripts/bump-only.sh pr in a new git repository
#       whose first commit is base/ and whose second is head/, with GITHUB_EVENT_NAME from `event`
#       (pull_request when there is no such file)
# Usage: scripts/selftest.sh
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

failed=0
count=0
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
stage() { # <case dir>: prints a copy of <case dir>/root with every _check.json renamed check.json
  local dest
  dest="$tmp/$count"
  mkdir -p "$dest"
  cp -R "$1/root/." "$dest/"
  find "$dest" -type f -name _check.json | while IFS= read -r f; do mv "$f" "$(dirname "$f")/check.json"; done
  echo "$dest"
}
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

output_case() { # <case dir> <command...>
  local dir="$1"; shift
  local got rc=0
  got="$("$@" 2>/dev/null)" || rc=$?
  count=$((count + 1))
  if [ "$rc" -eq 0 ] && [ "$got" = "$(cat "$dir/expect")" ]; then echo "ok   $dir prints $(tr '\n' ' ' < "$dir/expect")"
  else echo "FAIL $dir: exit $rc, printed: $got"; failed=1; fi
}

for c in selftest/graph-check/*/; do run_case "${c%/}" bash scripts/graph-check.sh "$(stage "${c%/}")"; done
for c in selftest/bump-only-file/*/; do run_case "${c%/}" bash scripts/bump-only.sh file "${c}old.json" "${c}new.json"; done
for c in selftest/bump-only-classify/*/; do output_case "${c%/}" bash scripts/bump-only.sh classify "${c}allow.json" "${c}diff"; done
for c in selftest/graphs/*/; do output_case "${c%/}" bash scripts/graphs.sh "$(stage "${c%/}")"; done
for c in selftest/bump-only-classify-fails/*/; do run_case "${c%/}" bash scripts/bump-only.sh classify "${c}allow.json" "${c}diff"; done
pr_repo() { # <case dir>: prints a git repository whose HEAD is head/ and HEAD^1 is base/
  local repo="$tmp/repo$count"
  mkdir -p "$repo"
  git -C "$repo" init -q
  cp -R "$1/base/." "$repo/"
  git -C "$repo" add -A
  git -C "$repo" -c user.name=selftest -c user.email=selftest@example.invalid commit -qm base
  find "$repo" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
  cp -R "$1/head/." "$repo/"
  git -C "$repo" add -A
  git -C "$repo" -c user.name=selftest -c user.email=selftest@example.invalid commit -qm head
  echo "$repo"
}
for c in selftest/bump-only-pr/*/; do
  event="pull_request"; [ -f "${c}event" ] && event="$(cat "${c}event")"
  repo="$(pr_repo "${c%/}")"
  run_case "${c%/}" env GITHUB_EVENT_NAME="$event" bash -c 'cd "$1" && bash "$2"/scripts/bump-only.sh pr' _ "$repo" "$root"
done

[ "$count" -gt 0 ] || { echo "no self-test case found"; exit 1; }
echo "$count cases"
exit "$failed"
