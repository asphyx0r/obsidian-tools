#!/usr/bin/env python3
"""Create the standard directory structure for an Obsidian vault."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Final, Sequence

SCRIPT_NAME: Final[str] = Path(__file__).name
SCRIPT_VERSION: Final[str] = "1.0.0"

WINDOWS_DEFAULT_ROOT: Final[Path] = Path(r"G:\Mon Drive\Obsidian")
LINUX_DEFAULT_ROOT: Final[Path] = Path.home() / "Obsidian"

RELATIVE_DIRECTORIES: Final[tuple[Path, ...]] = (
    Path("notes"),
    Path("notes", "inbox"),
    Path("notes", "fintech"),
    Path("notes", "work"),
    Path("notes", "work", "datalog"),
    Path("notes", "code"),
    Path("notes", "code", "python"),
    Path("notes", "code", "powershell"),
    Path("notes", "code", "bash"),
    Path("notes", "code", "sql"),
    Path("notes", "projects"),
    Path("notes", "projects", "prompts-source-control"),
    Path("notes", "hobbies"),
    Path("notes", "hobbies", "warhammer"),
    Path("notes", "hobbies", "magic-the-gathering"),
    Path("notes", "hobbies", "graffiti"),
    Path("templates"),
    Path("attachments"),
    Path("archive"),
    Path("sandbox"),
)

LOGGER = logging.getLogger(SCRIPT_NAME)


class CliError(ValueError):
    """Represent an invalid command-line invocation."""


def get_default_root() -> Path:
    """Return the platform-specific default Obsidian vault root."""
    if os.name == "nt":
        return WINDOWS_DEFAULT_ROOT

    return LINUX_DEFAULT_ROOT


def show_help() -> None:
    """Print the GNU-style command-line help."""
    print(
        f"""{SCRIPT_NAME} v{SCRIPT_VERSION}

usage: {SCRIPT_NAME} [-h] [--version] [--dry-run] [-v] [-r PATH]

Create the standard directory structure for an Obsidian vault.

options:
  -h, --help           show this help message and exit
  --version            show version and exit
  --dry-run            show the execution plan without side effects
  -v, --verbose        enable DEBUG console logging
  -r, --root PATH      set the Obsidian vault root directory
"""
    )


def parse_arguments(arguments: Sequence[str]) -> tuple[Path, bool, bool]:
    """Parse command-line arguments without external dependencies."""
    root_path = get_default_root()
    dry_run = False
    verbose = False

    index = 0
    while index < len(arguments):
        argument = arguments[index]

        if argument in ("-h", "--help"):
            show_help()
            raise SystemExit(0)

        if argument == "--version":
            print(f"{SCRIPT_NAME} v{SCRIPT_VERSION}")
            raise SystemExit(0)

        if argument == "--dry-run":
            dry_run = True
            index += 1
            continue

        if argument in ("-v", "--verbose"):
            verbose = True
            index += 1
            continue

        if argument in ("-r", "--root"):
            if index + 1 >= len(arguments):
                raise CliError(f"Option '{argument}' requires a path.")

            index += 1
            raw_root = arguments[index]

            if not raw_root.strip():
                raise CliError("The vault root path cannot be empty.")

            root_path = Path(os.path.expandvars(os.path.expanduser(raw_root)))
            index += 1
            continue

        if argument.startswith("--root="):
            raw_root = argument.removeprefix("--root=")

            if not raw_root.strip():
                raise CliError("The vault root path cannot be empty.")

            root_path = Path(os.path.expandvars(os.path.expanduser(raw_root)))
            index += 1
            continue

        raise CliError(f"Unknown option: {argument}")

    return root_path, dry_run, verbose


def configure_logging(verbose: bool) -> None:
    """Configure console logging."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )


def ensure_directory(path: Path, dry_run: bool) -> str:
    """Ensure that a directory exists and return its resulting status."""
    if path.exists():
        if not path.is_dir():
            raise NotADirectoryError(
                f"The path exists but is not a directory: {path}"
            )

        LOGGER.debug("Directory already exists: %s", path)
        return "existing"

    if dry_run:
        print(f"CREATE  {path}")
        return "planned"

    path.mkdir(parents=True, exist_ok=True)
    print(f"CREATED {path}")
    return "created"


def initialize_vault(root_path: Path, dry_run: bool) -> tuple[int, int, int]:
    """Create the vault directory structure."""
    resolved_root = root_path.absolute()

    LOGGER.debug("Vault root: %s", resolved_root)
    LOGGER.debug("Dry-run enabled: %s", dry_run)

    directories = (resolved_root,) + tuple(
        resolved_root / relative_path
        for relative_path in RELATIVE_DIRECTORIES
    )

    created_count = 0
    existing_count = 0
    planned_count = 0

    for directory in directories:
        status = ensure_directory(directory, dry_run)

        if status == "created":
            created_count += 1
        elif status == "existing":
            existing_count += 1
        elif status == "planned":
            planned_count += 1

    return created_count, existing_count, planned_count


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the program."""
    cli_arguments = sys.argv[1:] if arguments is None else arguments

    try:
        root_path, dry_run, verbose = parse_arguments(cli_arguments)
    except CliError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"ERROR: Run '{SCRIPT_NAME} --help' for usage information.",
            file=sys.stderr,
        )
        return 2

    configure_logging(verbose)

    try:
        created_count, existing_count, planned_count = initialize_vault(
            root_path=root_path,
            dry_run=dry_run,
        )
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print()

    if dry_run:
        print(
            "Dry-run completed: "
            f"{planned_count} directories would be created; "
            f"{existing_count} directories already exist."
        )
    else:
        print(
            "Completed: "
            f"{created_count} directories created; "
            f"{existing_count} directories already existed."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
