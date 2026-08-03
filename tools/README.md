# Repository tools

This directory contains repository maintenance tools shared with the
`git-starter-kit` core. Run commands from the repository root unless a tool
explicitly accepts another location.

## `backup-target-directory.py`

Creates a ZIP backup of a directory after staging an exact copy outside the
source tree. When the source is a Git repository, the archive name records the
captured commit and an exact SemVer tag when one points to that commit.

### Synopsis

```text
python tools/backup-target-directory.py [options] SOURCE TARGET
```

Display the complete interface:

```bash
python tools/backup-target-directory.py --help
```

### Examples

Preview an archive without copying data:

```bash
python tools/backup-target-directory.py \
  --dry-run \
  /path/to/source \
  /path/to/backups
```

Create the archive:

```bash
python tools/backup-target-directory.py \
  /path/to/source \
  /path/to/backups
```

The target and optional staging parent must remain outside the source. The
tool rejects symbolic links, existing output archives, invalid Git metadata,
and paths that would make the copy recursive.

## `git-init.sh` and `git-init.ps1`

The Bash and PowerShell initializers apply the same guarded workflow to an
existing, non-empty directory. They preview committable files, request explicit
confirmation, initialize `main`, validate the exact commit message through the
repository hooks, optionally create a SemVer tag, and push only when a remote
is supplied.

### Synopsis

```text
bash tools/git-init.sh [options]
powershell -NoProfile -File tools/git-init.ps1 [options]
```

Both tools expose the common leading options in this order:

```text
-h, --help
--version
--dry-run
-v, --verbose
```

Use `--path`, `--tag`, and `--remote` for the target-specific values. Run the
matching help command before initialization:

```bash
bash tools/git-init.sh --help
```

```powershell
powershell -NoProfile -File tools/git-init.ps1 --help
```

The tools stop before creating Git metadata when validation or confirmation
fails. They never bypass Commitlint or the repository hooks.

## `repository-audit.sh`

Runs the same repository validation profiles used by GitHub Actions.

### Synopsis

```text
bash tools/repository-audit.sh [all|full|readonly|markdown|spelling|static]
```

### Profiles

- `all` or `full`: run Markdown, spelling, and static validation.
- `readonly`: use installed tools without package installation or mutating
  smoke fixtures.
- `markdown`: run Markdownlint.
- `spelling`: run Codespell.
- `static`: run Git, Bash, PowerShell, workflow, secret-scanner, test, and
  commit-message validation.

The script validates release-aware commit ranges, the release triggers of the
agent-rules and repository-audit workflows, and the stable aggregate audit
job. Starter-kit-only package checks remain conditional on their files and do
not run in this downstream repository.

The `static` profile creates isolated temporary fixtures and may resolve pinned
Node packages. The `readonly` profile requires all commands to be installed and
fails explicitly when a required tool is unavailable.

## `verify-repository-audit-runs.py`

Waits for the exact successful push-triggered `Repository audit` runs required
by the guarded release workflow. It matches the workflow ID, commit SHA, refs,
event type, creation time, status, and conclusion.

### Synopsis

```text
python tools/verify-repository-audit-runs.py [options] \
  --repository OWNER/REPO \
  --workflow-id ID \
  --sha SHA \
  --ref REF \
  --created-after UTC
```

Repeat `--ref` when both a branch and tag run are required. The UTC lower bound
uses `YYYY-MM-DDTHH:MM:SSZ`.

### Examples

Preview the read-only query:

```bash
python tools/verify-repository-audit-runs.py \
  --dry-run \
  --repository asphyx0r/obsidian-tools \
  --workflow-id 123456 \
  --sha 0123456789abcdef0123456789abcdef01234567 \
  --ref main \
  --created-after 2026-08-03T20:00:00Z
```

Wait for the branch and tag audit runs:

```bash
python tools/verify-repository-audit-runs.py \
  --repository asphyx0r/obsidian-tools \
  --workflow-id 123456 \
  --sha 0123456789abcdef0123456789abcdef01234567 \
  --ref main \
  --ref v1.0.2 \
  --created-after 2026-08-03T20:00:00Z
```

Manual workflow runs never replace the required push events. A failed,
cancelled, ambiguous, or timed-out run returns a non-zero exit status.

## Validation expectations

Before committing tool changes, run the repository audit and the focused test
suites. At minimum, verify Python tests, the Bash commit-validation test,
Markdownlint, Codespell, Actionlint, Yamllint, ShellCheck, Shfmt, PowerShell
parsing, Ruff, Gitleaks, Betterleaks, and `git diff --check`.
