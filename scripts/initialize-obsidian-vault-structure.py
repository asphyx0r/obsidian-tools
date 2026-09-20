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
HINGE_ATTACHMENTS_DIRECTORY: Final[Path] = Path(
    "attachments", "notes", "profiles", "hinge"
)

RELATIVE_DIRECTORIES: Final[tuple[Path, ...]] = (
    Path("notes"),
    Path("notes", "inbox"),
    Path("notes", "goals"),
    Path("notes", "gtd"),
    Path("notes", "tasks"),
    Path("notes", "tasks", "daily"),
    Path("notes", "tasks", "backlogs"),
    Path("notes", "tasks", "recurring"),
    Path("notes", "recipes"),
    Path("notes", "profiles"),
    Path("notes", "books"),
    Path("notes", "books", "specifications"),
    Path("notes", "fintech"),
    Path("notes", "work"),
    Path("notes", "work", "datalog"),
    Path("notes", "ai"),
    Path("notes", "ai", "chatgpt"),
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
    Path("notes", "devtools", "github", "repositories"),
    Path("notes", "devtools", "vscode"),
    Path("notes", "devtools", "tmux"),
    Path("notes", "devtools", "psmux"),
    Path("notes", "projects"),
    Path("notes", "projects", "prompts-source-control"),
    Path("notes", "hobbies"),
    Path("notes", "hobbies", "warhammer"),
    Path("notes", "hobbies", "magic-the-gathering"),
    Path("notes", "hobbies", "graffiti"),
    Path("templates"),
    Path("templates", "gtd"),
    Path("templates", "profiles"),
    Path("attachments"),
    Path("attachments", "notes"),
    Path("attachments", "notes", "profiles"),
    HINGE_ATTACHMENTS_DIRECTORY,
    Path("archive"),
    Path("archive", "tasks"),
    Path("archive", "goals"),
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


@dataclass(frozen=True)
class _InitializationPlan:
    directories: tuple[Path, ...]
    directories_to_create: tuple[Path, ...]
    directories_existing: int
    gitkeep_to_create: tuple[Path, ...]
    gitkeep_existing: int


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
        f"{SCRIPT_NAME} v{SCRIPT_VERSION}\n\n"
        f"usage: {SCRIPT_NAME} [-h] [--version] [--dry-run] [-v] [-r PATH]\n\n"
        "Create the standard directory structure for an Obsidian vault.\n\n"
        "options:\n"
        "  -h, --help           show this help message and exit\n"
        "  --version            show version and exit\n"
        "  --dry-run            show the execution plan without side effects\n"
        "  -v, --verbose        enable DEBUG console logging\n"
        "  -r, --root PATH      set the Obsidian vault root directory\n"
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

            if raw_root.startswith("-"):
                raise CliError(
                    f"Option '{argument}' requires a path, not '{raw_root}'. "
                    "Use --root=PATH for a path starting with '-'."
                )

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


def _read_status(path: Path) -> os.stat_result | None:
    try:
        return path.lstat()
    except FileNotFoundError:
        return None


def _is_link(file_status: os.stat_result) -> bool:
    file_attributes = getattr(file_status, "st_file_attributes", 0)
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return stat.S_ISLNK(file_status.st_mode) or bool(
        file_attributes & reparse_point
    )


def is_directory_link(path: Path) -> bool:
    """Return whether path is a symbolic link or Windows reparse point."""
    file_status = _read_status(path)
    return file_status is not None and _is_link(file_status)


def _validate_directory_chain(path: Path) -> tuple[Path, ...]:
    """Validate ancestors without following links; return missing directories."""
    missing = []
    for directory in (*reversed(path.parents), path):
        file_status = _read_status(directory)
        if file_status is None:
            if directory.parent == directory:
                raise FileNotFoundError(f"The filesystem root is missing: {directory}")
            missing.append(directory)
            continue
        if _is_link(file_status):
            raise OSError(
                "The path is a directory link and will not be followed: "
                f"{directory}"
            )
        if not stat.S_ISDIR(file_status.st_mode):
            raise NotADirectoryError(
                f"The path exists but is not a directory: {directory}"
            )
        if not os.access(directory, os.X_OK):
            raise PermissionError(f"Directory traversal access denied: {directory}")
    return tuple(missing)


def _require_creation_access(path: Path) -> None:
    """Check observable access on the nearest existing parent, without writes."""
    for parent in path.parents:
        if _read_status(parent) is not None:
            if not os.access(parent, os.W_OK | os.X_OK):
                raise PermissionError(f"Directory creation access denied: {parent}")
            return
    raise FileNotFoundError(f"No existing parent directory: {path}")


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


def _plan_gitkeep_files(vault_root: Path) -> tuple[tuple[Path, ...], int]:
    """Plan empty note and Hinge placeholders without modifying the vault."""
    files_to_create = []
    existing_count = 0
    directories = (
        *get_note_subdirectories(vault_root),
        vault_root / HINGE_ATTACHMENTS_DIRECTORY,
    )

    for directory in directories:
        _validate_directory_chain(directory)
        gitkeep_path = directory / ".gitkeep"

        file_status = _read_status(gitkeep_path)
        if file_status is not None:
            if _is_link(file_status) or not stat.S_ISREG(file_status.st_mode):
                raise IsADirectoryError(
                    f"The path exists but is not a file (regular): {gitkeep_path}"
                )

            existing_count += 1
            continue

        has_existing_entries = directory.is_dir() and any(directory.iterdir())
        has_planned_child = any(
            candidate.parent == directory for candidate in directories
        )

        if has_existing_entries or has_planned_child:
            continue

        files_to_create.append(gitkeep_path)

    return tuple(files_to_create), existing_count


def _build_initialization_plan(root_path: Path) -> _InitializationPlan:
    _validate_directory_chain(root_path.absolute())
    # Check lexical ancestors before normalizing '..', which could hide a link.
    vault_root = Path(os.path.abspath(root_path))
    directories = (vault_root,) + tuple(
        vault_root / relative_path
        for relative_path in RELATIVE_DIRECTORIES
    )
    missing_directories: dict[Path, None] = {}
    existing_count = 0
    for directory in directories:
        missing = _validate_directory_chain(directory)
        missing_directories.update(dict.fromkeys(missing))
        if directory not in missing:
            existing_count += 1
            LOGGER.debug("Directory already exists: %s", directory)

    gitkeep_to_create, gitkeep_existing = _plan_gitkeep_files(vault_root)
    for path in (*missing_directories, *gitkeep_to_create):
        _require_creation_access(path)
    return _InitializationPlan(
        directories=directories,
        directories_to_create=tuple(missing_directories),
        directories_existing=existing_count,
        gitkeep_to_create=gitkeep_to_create,
        gitkeep_existing=gitkeep_existing,
    )


def _apply_initialization_plan(plan: _InitializationPlan) -> InitializationSummary:
    created_count = 0
    gitkeep_created = 0
    gitkeep_existing = plan.gitkeep_existing
    for directory in plan.directories_to_create:
        if directory not in _validate_directory_chain(directory):
            continue
        _require_creation_access(directory)
        directory.mkdir()
        print(f"CREATED {directory}")
        if directory in plan.directories:
            created_count += 1

    for gitkeep_path in plan.gitkeep_to_create:
        _validate_directory_chain(gitkeep_path.parent)
        file_status = _read_status(gitkeep_path)
        if file_status is not None:
            if _is_link(file_status) or not stat.S_ISREG(file_status.st_mode):
                raise IsADirectoryError(
                    f"The path exists but is not a file (regular): {gitkeep_path}"
                )
            gitkeep_existing += 1
            continue
        if any(gitkeep_path.parent.iterdir()):
            continue
        _require_creation_access(gitkeep_path)
        gitkeep_path.touch(exist_ok=False)
        print(f"CREATED {gitkeep_path}")
        gitkeep_created += 1

    return InitializationSummary(
        directories_created=created_count,
        directories_existing=len(plan.directories) - created_count,
        directories_planned=0,
        gitkeep_created=gitkeep_created,
        gitkeep_existing=gitkeep_existing,
        gitkeep_planned=0,
    )


def initialize_vault(root_path: Path, dry_run: bool) -> InitializationSummary:
    """Validate the whole initialization, then preview or apply its plan."""
    LOGGER.debug("Vault root: %s", root_path)
    LOGGER.debug("Dry-run enabled: %s", dry_run)
    plan = _build_initialization_plan(root_path)
    if dry_run:
        for path in (*plan.directories_to_create, *plan.gitkeep_to_create):
            print(f"CREATE  {path}")
        return InitializationSummary(
            directories_created=0,
            directories_existing=plan.directories_existing,
            directories_planned=len(plan.directories) - plan.directories_existing,
            gitkeep_created=0,
            gitkeep_existing=plan.gitkeep_existing,
            gitkeep_planned=len(plan.gitkeep_to_create),
        )

    try:
        return _apply_initialization_plan(plan)
    except (OSError, ValueError) as error:
        raise OSError(
            f"{error}. Initialization may be partial; no creations were rolled back."
        ) from error


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
