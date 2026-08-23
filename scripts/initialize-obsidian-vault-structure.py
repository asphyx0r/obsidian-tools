#!/usr/bin/env python3
"""Create the standard directory structure for an Obsidian vault."""

from __future__ import annotations

import logging
import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Sequence

SCRIPT_NAME: Final[str] = Path(__file__).name
SCRIPT_VERSION: Final[str] = "1.0.0"

WINDOWS_DEFAULT_ROOT: Final[Path] = Path(r"G:\Mon Drive\obsidian-vault")
LINUX_DEFAULT_ROOT: Final[Path] = Path.home() / "Obsidian"

RELATIVE_DIRECTORIES: Final[tuple[Path, ...]] = (
    Path("notes"),
    Path("notes", "inbox"),
    Path("notes", "books"),
    Path("notes", "books", "specifications"),
    Path("notes", "fintech"),
    Path("notes", "work"),
    Path("notes", "work", "datalog"),
    Path("notes", "code"),
    Path("notes", "code", "python"),
    Path("notes", "code", "powershell"),
    Path("notes", "code", "bash"),
    Path("notes", "code", "sql"),
    Path("notes", "devtools"),
    Path("notes", "devtools", "codex"),
    Path("notes", "devtools", "claude"),
    Path("notes", "devtools", "git"),
    Path("notes", "devtools", "github"),
    Path("notes", "devtools", "vscode"),
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


@dataclass(frozen=True)
class InitializationSummary:
    """Count directory and .gitkeep initialization outcomes."""

    directories_created: int
    directories_existing: int
    directories_planned: int
    gitkeep_created: int
    gitkeep_existing: int
    gitkeep_planned: int


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


def is_directory_link(path: Path) -> bool:
    """Return whether path is a symbolic link or Windows reparse point."""
    if path.is_symlink():
        return True

    try:
        file_status = path.stat(follow_symlinks=False)
    except FileNotFoundError:
        return False

    file_attributes = getattr(file_status, "st_file_attributes", 0)
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(file_attributes & reparse_point)


def ensure_directory(path: Path, dry_run: bool) -> str:
    """Ensure that a directory exists and return its resulting status."""
    if path.exists():
        if is_directory_link(path):
            raise OSError(
                f"The path is a directory link and will not be followed: {path}"
            )

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


def raise_walk_error(error: OSError) -> None:
    """Propagate an error raised while scanning note subdirectories."""
    raise error


def find_note_subdirectories(notes_root: Path) -> tuple[Path, ...]:
    """Return real subdirectories below the notes root without links."""
    if not notes_root.is_dir():
        return ()

    subdirectories: list[Path] = []

    for current_root, directory_names, _file_names in os.walk(
        notes_root,
        onerror=raise_walk_error,
        followlinks=False,
    ):
        current_path = Path(current_root)
        real_directory_names = []

        for directory_name in directory_names:
            directory = current_path / directory_name

            if is_directory_link(directory):
                continue

            real_directory_names.append(directory_name)
            subdirectories.append(directory)

        directory_names[:] = real_directory_names

    return tuple(sorted(subdirectories, key=lambda path: str(path).casefold()))


def get_note_subdirectories(vault_root: Path) -> tuple[Path, ...]:
    """Return existing and planned subdirectories below the notes root."""
    notes_root = vault_root / "notes"
    existing_directories = set(find_note_subdirectories(notes_root))
    planned_directories = {
        vault_root / relative_path
        for relative_path in RELATIVE_DIRECTORIES
        if relative_path.parts[0] == "notes" and len(relative_path.parts) > 1
    }
    directories = existing_directories | planned_directories
    return tuple(sorted(directories, key=lambda path: str(path).casefold()))


def uses_directory_link(path: Path, notes_root: Path) -> bool:
    """Return whether path is or is below a symbolic directory link."""
    current_path = path

    while current_path != notes_root:
        if is_directory_link(current_path):
            return True

        current_path = current_path.parent

    return False


def ensure_gitkeep_files(vault_root: Path, dry_run: bool) -> tuple[int, int, int]:
    """Ensure that empty note subdirectories contain a .gitkeep file."""
    created_count = 0
    existing_count = 0
    planned_count = 0
    notes_root = vault_root / "notes"
    directories = get_note_subdirectories(vault_root)

    for directory in directories:
        if uses_directory_link(directory, notes_root):
            continue

        gitkeep_path = directory / ".gitkeep"

        if gitkeep_path.exists():
            if not gitkeep_path.is_file():
                raise IsADirectoryError(
                    f"The path exists but is not a file: {gitkeep_path}"
                )

            existing_count += 1
            continue

        has_existing_entries = directory.is_dir() and any(directory.iterdir())
        has_planned_child = any(
            candidate.parent == directory for candidate in directories
        )

        if has_existing_entries or has_planned_child:
            continue

        if dry_run:
            print(f"CREATE  {gitkeep_path}")
            planned_count += 1
            continue

        gitkeep_path.touch(exist_ok=False)
        print(f"CREATED {gitkeep_path}")
        created_count += 1

    return created_count, existing_count, planned_count


def initialize_vault(root_path: Path, dry_run: bool) -> InitializationSummary:
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

    gitkeep_created, gitkeep_existing, gitkeep_planned = ensure_gitkeep_files(
        resolved_root,
        dry_run,
    )

    return InitializationSummary(
        directories_created=created_count,
        directories_existing=existing_count,
        directories_planned=planned_count,
        gitkeep_created=gitkeep_created,
        gitkeep_existing=gitkeep_existing,
        gitkeep_planned=gitkeep_planned,
    )


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
        summary = initialize_vault(
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
            f"{summary.directories_planned} directories would be created; "
            f"{summary.directories_existing} directories already exist; "
            f"{summary.gitkeep_planned} .gitkeep files would be created; "
            f"{summary.gitkeep_existing} .gitkeep files already exist."
        )
    else:
        print(
            "Completed: "
            f"{summary.directories_created} directories created; "
            f"{summary.directories_existing} directories already existed; "
            f"{summary.gitkeep_created} .gitkeep files created; "
            f"{summary.gitkeep_existing} .gitkeep files already existed."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
