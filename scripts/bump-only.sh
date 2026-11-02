#!/usr/bin/env bash
# A pull request that touches only allowlisted paths may auto-merge, so it must be a date bump and
# nothing else: every changed file is a modified node whose only changed lines are measuredAt and
# attrs.fetched_at, with the new measuredAt the date of the new fetched_at, and fetched_at later
# than before. Any other change to a fact fails unless the pull request also touches a path outside
# the allowlist (such as the vendor's CHANGES.md); it then cannot auto-merge, so a maintainer
# reviews it. The generated INDEX.md holds no measurement date, so a date bump leaves it unchanged.
# A bump is also bound to evidence of a fetch: the pull request adds exactly one refresh report per graph
# it touches, <graph>/graph/refresh/<run id>.json, which must name a commit that is an ancestor of the base
# with the node unchanged since, pass scripts/report-check.py under the base's policy/sources.json, and hold
# an unchanged result for each bumped node, for its source, fetched exactly at the node's new fetched_at.
#
# Usage:
#   scripts/bump-only.sh pr                       in CI, on the pull request's merge commit
#   scripts/bump-only.sh classify <allow> <diff>  prints review, bump or reject
#       <allow>  a file holding the JSON array of allowlisted paths (an entry ending in / is a prefix)
#       <diff>   a file holding `git diff --no-renames --name-status` output
#   scripts/bump-only.sh file <old> <new>         exit 0 when <new> is a date bump of <old>
set -euo pipefail

die() { echo "$*" >&2; exit 1; }

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Where a graph keeps its refresh reports, from the checker's own policy/constants.json.
reports_dir="$(jq -er '.graphPaths.reports' "$here/../policy/constants.json")" || die "policy/constants.json has no graphPaths.reports"
report_path="/$reports_dir/[0-9]+\\.json\$"

classify() { # review: a maintainer reviews it; bump: every file must be a date bump; reject: fails
  # A bump may add the refresh report that supports it, and only that: a report is added, never modified.
  local allow="$1" diff="$2" verdict
  verdict="$(jq -Rrn --slurpfile allow "$allow" --arg report "$report_path" '
    [inputs | select(length > 0) | split("\t") | {status: .[0], path: .[1]}] as $changes
    | def allowed($f): any($allow[0][]; . as $p | if ($p | endswith("/")) then ($f | startswith($p)) else $f == $p end);
    if ($changes | length) == 0 then "review"
    elif any($changes[]; allowed(.path) | not) then "review"
    elif any($changes[]; .status == "M") and all($changes[]; .status == "M" or (.status == "A" and (.path | test($report)))) then "bump"
    else "reject" end' "$diff")" || die "classify: unreadable input"
  echo "$verdict"
}

bound_to_report() { # <tmp> <diff>: the bump is supported by one valid refresh report per graph it touches
  local tmp="$1" diff="$2" path graph report n=0 base
  base="$(git rev-parse HEAD^1)"
  git show HEAD^1:policy/sources.json > "$tmp/sources.json" 2>/dev/null || die "the base commit has no policy/sources.json"
  git show HEAD^1:policy/source-scopes.json > "$tmp/scopes.json" 2>/dev/null || die "the base commit has no policy/source-scopes.json"
  while IFS=$'\t' read -r status path; do
    [ "$status" = M ] || continue
    graph="${path%%/graph/*}"
    report="$(awk -F'\t' -v g="$graph/$reports_dir/" '$1 == "A" && index($2, g) == 1 {print $2}' "$diff")"
    [ "$(wc -l <<<"$report" | tr -d ' ')" = 1 ] && [ -n "$report" ] || die "$path: the pull request must add exactly one refresh report under $graph/$reports_dir/"
    git show "HEAD:$report" > "$tmp/report.json"
    git show "HEAD^1:$path" > "$tmp/old.json"
    git show "HEAD:$path" > "$tmp/new.json"
    jq -e --arg g "$graph" '.graph == $g' "$tmp/report.json" >/dev/null || die "$report: its graph is not $graph"
    n=$((n + 1))
    # The report names the commit it read: an ancestor of the base, with this node unchanged since.
    local rc
    rc="$(jq -r '.commit' "$tmp/report.json")"
    git merge-base --is-ancestor "$rc" "$base" 2>/dev/null || die "$report: its commit $rc is not an ancestor of the base commit"
    git diff --quiet "$rc" "$base" -- "$path" || die "$path: changed between the report's commit and the base commit"
    python3 "$here/report-check.py" check "$tmp/report.json" "$tmp/sources.json" "$tmp/scopes.json" "$rc" || die "$report: not valid under policy/sources.json"
    python3 "$here/report-check.py" bump "$tmp/report.json" "$tmp/old.json" "$tmp/new.json" || die "$path: the report does not support this bump"
  done < "$diff"
  [ "$n" -gt 0 ] || die "a date bump needs a modified node"
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
      bound_to_report "$tmp" "$tmp/diff"
      while IFS=$'\t' read -r status path; do
        [ "$status" = M ] || continue # an added file is its report, checked above
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
