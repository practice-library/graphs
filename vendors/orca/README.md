# vendors/orca

Facts about the Orca command-line interface (`orca`), read from the public repository `stablyai/orca` (MIT) at one pinned commit. One fact per file in `graph/nodes/`, listed in `INDEX.md`. The scope, questions and slices are in #64.

This is **slice 1 of 4**: the `worktree`, `terminal`, `terminal-daemon` and `orchestration` command groups, 50 commands in all.

## Pin

- **Tag:** `v1.4.245`.
- **Commit:** `1c6ac8c3c4d2c3dec2cb5966d225ca2a0e0471d3`, committed 2026-10-30 (`release.orca.cli.1-4-245`).
- **Rule:** every quote is read from a file at this commit. A newer release is a new pin, not an edit.

## Sources

Only two hosts, both recorded in `policy/sources.json`:
- **`raw.githubusercontent.com`:** files at the pinned commit:
  - command definitions: `src/cli/specs/` (core, orchestration, orchestration workers, terminal close, send, daemon and pane title, worktree set, listing notes);
  - CLI behaviour: `src/cli/` (output, errors, entry point, worktree removal request and warnings, terminal handlers, worktree ps verdicts);
  - shared types and host code: `src/shared/` (envelope, flags, worktree contracts, status rollup) and `src/main/` (worktree removal and its preflight, status projection);
  - documentation: `docs/site/content/docs/cli/` (overview, orchestration, reference);
  - `LICENSE`.
- **`api.github.com`:** the commit endpoint, for the release date.

The project's website is not cited. On 2026-11-01 its `/robots.txt` returned an HTML page, not a robots file (#64).

## How the commands are covered

- **One node per command:** `capability.orca.cli.<group>.<command>`.
  - Quote: the command's summary from its spec.
  - `scope`: its usage line.
  - Note: its effect (reads, writes or removes) and its flags beyond the global ones, and whether its spec marks it destructive.
- **Behaviour:** `rule`, `permission` and `limit` nodes, each with `appliesTo` or `limits` edges to the command nodes.
- **Effect class:** "Effect" in a note is this repository's reading of the spec and the code, not an upstream field. Only "Marked destructive" quotes an upstream marker (`destructive: true`).
- **Gaps:** a question the files do not answer is recorded as `unknown`, with a note starting "Absent: ".

## Questions answered (#64)

Breadth (questions 1 to 6) for the four groups:
1. **Coverage:** all 50 commands in the four groups have a capability node. The not-covered list is below.
2. **What each does:** the summary is in each capability node's quote, and the usage and flags are in its scope and note.
3. **Output:**
   - `rule.orca.cli.json-output`;
   - `rule.orca.cli.json-success-envelope`;
   - `rule.orca.cli.json-failure-envelope`;
   - `rule.orca.cli.local-error-envelope`.
4. **Errors:** `rule.orca.cli.error-exit-code`. `rule.orca.cli.error-codes` is `unknown`: no catalogue was found, and its note lists the codes the files name. #64 named `src/cli/cli-exit-code.ts`, which does not exist at the pinned commit. Commands with their own exit rules have their own nodes.
5. **Effects:** in each capability node's note.
6. **Force:** in these groups only `worktree rm` takes `--force`: `permission.orca.cli.worktree-rm-force` and `permission.orca.cli.worktree-rm-force-pty`. `rule.orca.cli.worktree-rm-hook-failure` is what `--force` does not waive. `terminal-daemon restart` requires `--yes`.

Depth:

7. **worktree create:**
   - `rule.orca.cli.worktree-create-checkout`, `-branch`, `-default-base`, `-terminal`, `-parent` and `-retry`;
   - `-folder` is `unknown`: the folder location is not stated.
8. **worktree rm:**
   - `rule.orca.cli.worktree-rm-dirty` (refused without `--force`);
   - `-submodule`, `-branch`, `-unmerged`, `-kept-branch`, `-folder`, `-hooks`, `-hook-failure` and `-in-progress`;
   - the two `--force` permissions.
9. **States:**
   - `rule.orca.cli.worktree-status-values` (`active`, `working`, `permission`, `done`, `inactive`; there is no idle or busy);
   - `-status-heuristic` and `-status-merge` (the row takes the highest status of its terminals: permission, working, done, active, inactive);
   - `-sidebar-status` (the optional sidebar field, which has more values) and `worktree-ps-terminal-verdict`;
   - `worktree-listing-scope`.
10. **worktree set:** `rule.orca.cli.worktree-set-fields`. Where the metadata is stored is not stated.
11. **Handles:** `rule.orca.cli.terminal-handle-server` and `terminal-handle-lifetime` (runtime-scoped: reacquire after a restart).
12. **create, send and wait:** `rule.orca.cli.terminal-create-tab`, `terminal-send-raw`, `terminal-send-retry` and `terminal-wait-exit` (exit 1 when not satisfied).
13. **Encoding:**
    - `rule.orca.cli.terminal-read-stripped` (escape sequences are stripped by default);
    - `terminal-read-json` (read and list print through the shared JSON printer);
    - `json-output` (`JSON.stringify`, which escapes U+0000 to U+001F);
    - `check-keepalive`: `check --wait` writes JSON lines to stderr, which mix into the output if stderr is merged with stdout.
14. **close:** `rule.orca.cli.terminal-close-scope`, `terminal-close-all` and `terminal-close-unverifiable` (bulk close fails if it cannot confirm every terminal stopped).
15. **Daemon:** `rule.orca.cli.terminal-daemon-restart` (ends every process), `terminal-daemon-recheck` and `terminal-daemon-status`.
16. **Projects, repos and references:** answered in slice 2.
17. **What removing a project deletes:** answered in slice 2.
18. **Workers:**
    - `rule.orca.cli.worker-start-exit` and `worker-start-setup`;
    - `worker-stop-keeps`, `worker-release-scope` and `worker-release-idempotent`;
    - `worker-retain`, `worker-abandon` and `worker-terminal-state`.
19. **Runs, tasks, gates and reset:**
    - `rule.orca.cli.run`, `task-statuses`, `gate` and `reset`;
    - `coordinator-retired` and `request-show-absent`.
20. **Messages:** `rule.orca.cli.send-types`. `message-store` is `unknown`: no storage location or retention period is stated.
21. **check:**
    - `rule.orca.cli.check-default`, `check-replay`, `check-types` (the wake condition for `--wait`; it filters only `--peek` and `--all`) and `check-keepalive`;
    - `limit.orca.cli.check-peek-rows`.

Limits: `limit.orca.cli.ask-timeout` (30 minutes), `check-peek-rows`, `worker-list-rows`, `task-list-brief` and `terminal-read-default-lines`.

## Not covered in this slice

These are 238 of the 288 commands that `orca agent-context --json` lists at the pinned tag. They follow in slices 2 to 4.
- **Unnamed commands:** four commands are counted but not named here: one top-level command and the three `speech` commands. Each name contains a word this organisation's content denylist rejects (#64).
- **Hidden command:** a hidden, deprecated `terminal stop` is defined in the spec but absent from that list, so it is not a node.

- `account` (4): `add`, `list`, `rm`, `select`.
- `agent` (5): `hooks off`, `hooks on`, `hooks prepare-codex`, `hooks status`, `launch`.
- `artifacts` (5): `delete`, `list`, `share`, `unshare`, `update`.
- `automations` (7): `create`, `edit`, `list`, `remove`, `run`, `runs`, `show`.
- `browser` (2): `identity get`, `identity set`.
- `capture` (2): `start`, `stop`.
- `clipboard` (2): `read`, `write`.
- `computer` (14): `capabilities`, `click`, `drag`, `get-app-state`, `hotkey`, `list-apps`, `list-windows`, `paste-text`, `perform-secondary-action`, `permissions`, `press-key`, `scroll`, `set-value`, `type-text`.
- `cookie` (3): `delete`, `get`, `set`.
- `diagnostics` (1): `memory`.
- `dialog` (2): `accept`, `dismiss`.
- `emulator` (16): `attach`, `ax`, `button`, `devices`, `exec`, `gesture`, `install`, `kill`, `launch`, `list`, `logcat`, `permissions`, `rotate`, `shutdown`, `tap`, `type`.
- `environment` (11): `add`, `cancel-stop`, `forget`, `list`, `recover`, `rm`, `rollback`, `show`, `status`, `stop`, `update`.
- `file` (3): `diff`, `open`, `open-changed`.
- `host` (2): `list`, `name`.
- `intercept` (3): `disable`, `enable`, `list`.
- `jira` (21): `assignee clear`, `assignee list`, `assignee set`, `comment add`, `comment list`, `connection`, `create`, `issue`, `label add`, `label rm`, `label set`, `list`, `priority clear`, `priority list`, `priority set`, `project fields`, `project list`, `project types`, `search`, `status list`, `status set`.
- `linear` (29): `assignee clear`, `assignee set`, `attach`, `comment add`, `comment delete`, `comment edit`, `create`, `due-date clear`, `due-date set`, `estimate clear`, `estimate set`, `issue`, `label add`, `label remove`, `label set`, `list`, `list-issues`, `priority clear`, `priority set`, `project list`, `relation add`, `relation remove`, `save-issue`, `search`, `status set`, `team labels`, `team list`, `team members`, `team states`.
- `mouse` (4): `down`, `move`, `up`, `wheel`.
- `profile` (2): `state exports`, `state rollback`.
- `project` (7): `list`, `setup-clone`, `setup-create`, `setup-delete`, `setup-existing-folder`, `setup-update`, `setups`.
- `reference` (4): `add`, `find`, `list`, `remove`.
- `repo` (6): `add`, `list`, `search-refs`, `set`, `set-base-ref`, `show`.
- `serve` (5): `serve` itself, `restore resume`, `service install`, `service status`, `service uninstall`.
- `set` (5): `credentials`, `device`, `headers`, `media`, `offline`.
- `skills` (6): `get`, `install`, `installed`, `list`, `share`, `update`.
- `speech` (3): counted, not named. Their names contain a word the content denylist rejects.
- `storage` (6): `local clear`, `local get`, `local set`, `session clear`, `session get`, `session set`.
- `tab` (13): `close`, `create`, `current`, `list`, `profile clone`, `profile create`, `profile delete`, `profile list`, `profile set`, `profile show`, `profile use-default`, `show`, `switch`.
- `vm` (1): `recipe doctor`.
- Single-word commands (43): `agent-context`, `back`, `check`, `clear`, `click`, `console`, `dblclick`, `download`, `drag`, `eval`, `exec`, `fill`, `find`, `focus`, `forward`, `full-screenshot`, `geolocation`, `get`, `goto`, `highlight`, `hover`, `inserttext`, `is`, `keypress`, `network`, `open`, `open-url`, `pdf`, `ports`, `reload`, `screenshot`, `scroll`, `scrollintoview`, `search`, `select`, `select-all`, `snapshot`, `status`, `type`, `uncheck`, `upload`, `viewport`, `wait`.

## Attribution

The quoted passages are from the `stablyai/orca` repository, Copyright (c) 2026 Lovecast Inc., under the MIT License. The quotes are short and unmodified, and each links to its file at the pinned commit. The ids, names, verdicts, values and edges around them are this repository's own. The project does not endorse this repository.
