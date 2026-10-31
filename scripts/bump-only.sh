#!/usr/bin/env bash
# A pull request that touches only allowlisted paths may auto-merge, so it must be a date bump and
# nothing else: every changed file is a modified node whose only changed lines are measuredAt and
# attrs.fetched_at, with the new measuredAt the date of the new fetched_at, and fetched_at later
# than before. Any other change to a fact fails unless the pull request also touches a path outside
# the allowlist (such as the vendor's regenerated INDEX.md); it then cannot auto-merge, so a
# maintainer reviews it.
#
# Usage:
#   scripts/bump-only.sh pr                       in CI, on the pull request's merge commit
#   scripts/bump-only.sh classify <allow> <diff>  prints review, bump or reject
#       <allow>  a file holding the JSON array of allowlisted paths (an entry ending in / is a prefix)
#       <diff>   a file holding `git diff --no-renames --name-status` output
#   scripts/bump-only.sh file <old> <new>         exit 0 when <new> is a date bump of <old>
set -euo pipefail

die() { echo "$*" >&2; exit 1; }

classify() { # review: a maintainer reviews it; bump: every file must be a date bump; reject: fails
  local allow="$1" diff="$2" verdict
  verdict="$(jq -Rrn --slurpfile allow "$allow" '
    [inputs | select(length > 0) | split("\t") | {status: .[0], path: .[1]}] as $changes
    | def allowed($f): any($allow[0][]; . as $p | if ($p | endswith("/")) then ($f | startswith($p)) else $f == $p end);
    if ($changes | length) == 0 then "review"
    elif any($changes[]; allowed(.path) | not) then "review"
    elif all($changes[]; .status == "M") then "bump"
    else "reject" end' "$diff")" || die "classify: unreadable input"
  echo "$verdict"
}

file_check() { # <old> <new>
  local old="$1" new="$2" bad
  jq -e 'type == "object"' "$old" >/dev/null 2>&1 || die "$old: not a JSON object"
  jq -e 'type == "object"' "$new" >/dev/null 2>&1 || die "$new: not a JSON object"
  jq -en --slurpfile o "$old" --slurpfile n "$new" '
    ($o[0] | del(.measuredAt, .attrs.fetched_at)) == ($n[0] | del(.measuredAt, .attrs.fetched_at))' >/dev/null \
    || die "a field other than measuredAt or attrs.fetched_at changed"
  bad="$(git diff --no-index -U0 -- "$old" "$new" | grep -E '^[+-]' | grep -vE '^(\+\+\+|---) ' \
    | grep -vE '^[+-][[:space:]]*"(measuredAt|fetched_at)": "[^"]*",?$' || true)"
  [ -z "$bad" ] || die "a changed line is not measuredAt or fetched_at: $(head -1 <<<"$bad")"
  jq -en --slurpfile n "$new" '($n[0].measuredAt | type) == "string" and $n[0].measuredAt == ($n[0].attrs.fetched_at[0:10])' >/dev/null \
    || die "measuredAt is not the date of fetched_at"
  jq -en --slurpfile o "$old" --slurpfile n "$new" '$n[0].attrs.fetched_at > $o[0].attrs.fetched_at' >/dev/null \
    || die "fetched_at is not later than before"
  echo "ok $new is a date bump"
}

pr() {
  [ "${GITHUB_EVENT_NAME:-}" = pull_request ] || { echo "not a pull request: nothing to check"; return 0; }
  local tmp verdict path
  tmp="$(mktemp -d)"
  # The allowlist auto-merge uses: .github/automerge-paths.json on the base commit, none when absent.
  if git cat-file -e HEAD^1:.github/automerge-paths.json 2>/dev/null; then
    git show HEAD^1:.github/automerge-paths.json | jq -c '.paths' > "$tmp/allow" || die "main's .github/automerge-paths.json is not valid JSON"
  else
    echo '[]' > "$tmp/allow"
  fi
  jq -e 'type == "array"' "$tmp/allow" >/dev/null || die "main's .github/automerge-paths.json has no paths array"
  git diff --no-renames --name-status HEAD^1 HEAD > "$tmp/diff"
  verdict="$(classify "$tmp/allow" "$tmp/diff")"
  case "$verdict" in
    review) echo "touches a path outside the allowlist: a maintainer reviews it" ;;
    reject) die "touches only allowlisted paths but adds, deletes or renames a file: $(cat "$tmp/diff")" ;;
    bump)
      while IFS=$'\t' read -r _ path; do
        git show "HEAD^1:$path" > "$tmp/old.json"
        git show "HEAD:$path" > "$tmp/new.json"
        file_check "$tmp/old.json" "$tmp/new.json" >/dev/null || die "$path is not a date bump"
        echo "ok $path"
      done < "$tmp/diff"
      ;;
    *) die "unexpected verdict $verdict" ;;
  esac
}

case "${1:-}" in
  pr) pr ;;
  classify) [ $# -eq 3 ] || die "usage: scripts/bump-only.sh classify <allow> <diff>"; classify "$2" "$3" ;;
  file) [ $# -eq 3 ] || die "usage: scripts/bump-only.sh file <old> <new>"; file_check "$2" "$3" ;;
  *) die "usage: scripts/bump-only.sh pr | classify <allow> <diff> | file <old> <new>" ;;
esac
