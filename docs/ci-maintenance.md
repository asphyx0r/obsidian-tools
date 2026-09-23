# CI maintenance

## Repository policy

`Repository audit` validates every pushed branch, version tags matching `v*`,
pull requests targeting `main` or `master`, and published releases. Each event
validates its own revision. Passing an earlier run does not validate a later
commit or guarantee that a future update will pass.

Project checks include quality dependency coherence on Linux and Windows.
The registry, direct declarations and lockfiles must agree before an update can
pass the aggregate audit. The application remains a `project` with `deployment`
release artifacts.

Automatic agent-rule synchronization is disabled through
`automations.agentRulesSync: false`. The distributed workflow remains available
for a future explicit opt-in; it must also be disabled in GitHub Actions after
this configuration reaches `main`. Guarded PR merging and release preflight
remain enabled in the configuration. Guarded merging uses the existing App
credentials independently of agent-rule synchronization. Its external rulesets
are not activated: this repository retains its existing GitHub protections and
merge settings. Until separately authorized activation, use the ordinary PR
merge path with the required `Repository audit` check and a validated squash
message. The installed guarded workflow must not be described as enforced.
See [the guarded merge guide](guarded-pull-request-merges.md) for activation.

## Dependency updates

Dependabot proposes updates using the accepted `chore(tools)` prefix. It does
not maintain this repository's complete version registry, and its generated
headers can exceed the 50-character limit. An invalid proposal must remain red
until a maintainer prepares a coherent replacement. Do not exempt bot commits
from Commitlint or merge a partial dependency update.

For each accepted proposal:

1. Update the corresponding entries in `tools/quality/versions.json` and the
   direct declarations in `requirements.in` or `package.json`.
2. Regenerate the affected lockfile with the supported toolchain. Keep unrelated
   dependency versions stable and preserve the `smol-toml` security override.
3. Install with hash enforcement for Python and `npm ci --ignore-scripts` for
   Node. Run `python -B tools/quality/check-versions.py`, the project checks and
   the repository audit.
4. Commit with an accepted scope and a header no longer than 50 characters,
   for example `chore(tools): update quality dependencies`.
5. Require successful CI at the replacement PR's exact head before integration.
   Close superseded proposals only after verifying their accepted changes in
   `main`.

The maintenance update accepts Coverage 7.16.1, Ruff 0.16.8, Commitlint 21.2.3 and
Markdownlint CLI2 0.23.3 from proposals #9 through #12. Python lock generation uses
Python 3.11 and targeted `pip-compile --upgrade-package` selections. CI also
installs the resulting hash-locked requirements on Windows with Python 3.14.

## Local core adaptations

The [v2.11.2 migration record](core-upgrade-v2.11.2.md) is historical provenance.
This maintenance adds a project coherence check and broadens the audit workflow's
push filter to all branches. Its executable contract accepts that filter while
retaining permissions, tag and release events, revision selection and job gates.
The contract also records the migration's existing project dependency installation
and Windows shell-linter steps, which its previous contract had omitted.
Dependabot prefixes, quality versions and their locks are also project overlays.

These adaptations do not change the recorded canonical starter-kit version or
archive digest. They must be reviewed during future upgrades; this repository is
not an exact copy of the upstream package.
