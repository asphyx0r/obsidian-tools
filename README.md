# obsidian-tools

`obsidian-tools` provides a Python command-line tool that creates a standard
directory structure for an Obsidian vault. Existing directories are preserved,
so the command can be run again safely when the vault structure already exists.

## Features

- Creates the repository's standard notes, templates, attachments, archive,
  and sandbox directories.
- Adds a zero-byte `.gitkeep` file to every empty subdirectory below `notes/`,
  including empty custom subdirectories found at runtime, and to the empty
  `attachments/notes/profiles/hinge/` directory.
- Supports a side-effect-free `--dry-run` preview.
- Validates planned paths and observable access before creating anything.
- Accepts an explicit vault root on Windows, Linux, and macOS.
- Reports directory and `.gitkeep` outcomes separately.

## Requirements

- Python 3.10 or later.

No third-party Python package is required.

## Usage

Run the tool from the repository root and provide the target vault explicitly:

```bash
python scripts/initialize-obsidian-vault-structure.py \
  --root /path/to/Obsidian
```

Preview the same operation without creating directories:

```bash
python scripts/initialize-obsidian-vault-structure.py \
  --dry-run \
  --root /path/to/Obsidian
```

Use `--help` to display every supported option:

```bash
python scripts/initialize-obsidian-vault-structure.py --help
```

When `--root` is omitted, the default is `G:\Mon Drive\obsidian-vault` on
Windows and `~/Obsidian` on other platforms.

The `--root` and `-r` options require a path, not another option. For a path
starting with a hyphen, use `--root=-name` or `--root ./-name`.

Simulation and execution share the same preflight checks. Files blocking
directory paths, invalid `.gitkeep` entries, inaccessible note directories,
and directory links in managed paths or their ancestors cause an error before
any creation. Missing ancestors of the selected root are included in the
preview and created when needed. Directory counts cover the vault root and
the declared structure, excluding ancestors outside the vault.

Access checks do not create probe files and cannot guarantee that a later
write will succeed. Permissions, concurrent changes, or disk failures may
still interrupt execution. Such errors report that initialization may be
partial; created entries are not rolled back. A complete vault needs no write
access when nothing needs to be created. Exit codes are `0` for success, `1`
for filesystem or initialization errors, and `2` for invalid arguments.

## Directory structure

The tool creates the following default notes tree:

```text
notes/
|-- inbox/
|-- goals/
|-- gtd/
|-- tasks/
|   |-- daily/
|   |-- backlogs/
|   `-- recurring/
|-- recipes/
|-- profiles/
|-- books/
|   `-- specifications/
|-- fintech/
|-- work/
|   `-- datalog/
|-- code/
|   |-- python/
|   |-- powershell/
|   |-- bash/
|   `-- sql/
|-- devtools/
|   |-- codex/
|   |-- claude/
|   |-- git/
|   |-- github/
|   |   `-- repositories/
|   |-- vscode/
|   |-- tmux/
|   `-- psmux/
|-- projects/
|   `-- prompts-source-control/
`-- hobbies/
    |-- warhammer/
    |-- magic-the-gathering/
    `-- graffiti/
```

It also creates the top-level `templates/`, `attachments/`, `archive/`, and
`sandbox/` directories, including `templates/gtd/`, `templates/profiles/`,
`archive/tasks/`, `archive/goals/`, and
`attachments/notes/profiles/hinge/` with its parents. Empty subdirectories below
`notes/` and the empty Hinge directory receive a zero-byte `.gitkeep`. Other
attachment directories do not receive `.gitkeep` files. Existing files and
existing regular `.gitkeep` contents are never modified. A `.gitkeep` that is
a directory, link, or other non-regular entry is rejected. Directory links and
Windows reparse points in the root, its ancestors, or managed directories are
rejected; linked custom note directories are skipped. The system directories `.githooks/`,
`.github/`, `.GitHub/`, and `.obsidian/` are not managed by the tool.

A new vault contains 47 directories including its root and 27 empty
`.gitkeep` files. The initializer does not create notes, template contents,
or attachments; the template subdirectories do not receive `.gitkeep` files.

Review the `--dry-run` output before using the default structure with an
existing vault.

The `notes/gtd/` directory is intended for GTD sorting files. Create
`next-actions.md`, `waiting-for.md`, `someday.md`, and `weekly-review.md`
manually in this directory; the tool does not create these Markdown files.

## Contributing

This is a personal repository. Contributions are reviewed on a case-by-case
basis. See [CONTRIBUTING.md](CONTRIBUTING.md) for repository checks and commit
requirements.

## License

This project is licensed under the [MIT License](LICENSE).
