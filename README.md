# obsidian-tools

`obsidian-tools` provides a Python command-line tool that creates a standard
directory structure for an Obsidian vault. Existing directories are preserved,
so the command can be run again safely when the vault structure already exists.

## Features

- Creates the repository's standard notes, templates, attachments, archive,
  and sandbox directories.
- Supports a side-effect-free `--dry-run` preview.
- Accepts an explicit vault root on Windows, Linux, and macOS.
- Reports created, existing, and planned directories.

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

When `--root` is omitted, the default is `G:\Mon Drive\Obsidian` on Windows
and `~/Obsidian` on other platforms.

## Directory structure

The tool creates top-level directories for notes, templates, attachments,
archives, and sandbox content. The notes tree includes inbox, work, code,
projects, fintech, and hobby categories defined by the script.

Review the `--dry-run` output before using the default structure with an
existing vault.

## Contributing

This is a personal repository. Contributions are reviewed on a case-by-case
basis. See [CONTRIBUTING.md](CONTRIBUTING.md) for repository checks and commit
requirements.

## License

This project is licensed under the [MIT License](LICENSE).
