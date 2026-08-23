import importlib.util
import io
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "initialize-obsidian-vault-structure.py"
)
SPEC = importlib.util.spec_from_file_location(
    "initialize_obsidian_vault_structure",
    MODULE_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load Obsidian vault initializer.")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class InitializeObsidianVaultStructureTests(unittest.TestCase):
    def initialize(self, root, dry_run=False):
        output = io.StringIO()

        with redirect_stdout(output):
            result = MODULE.initialize_vault(root, dry_run=dry_run)

        return result, output.getvalue()

    def run_main(self, arguments):
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = MODULE.main(arguments)

        return exit_code, stdout.getvalue(), stderr.getvalue()

    def snapshot(self, root):
        records = []

        for path in sorted(root.rglob("*")):
            relative_path = path.relative_to(root).as_posix()

            if path.is_dir():
                records.append(("directory", relative_path))
            else:
                records.append(("file", relative_path, path.read_bytes()))

        return tuple(records)

    def create_directory_link(self, link_path, link_target):
        if os.name == "nt":
            result = subprocess.run(
                [
                    "cmd.exe",
                    "/d",
                    "/c",
                    "mklink",
                    "/J",
                    str(link_path),
                    str(link_target),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                self.skipTest(
                    f"Directory junctions are unavailable: {result.stderr}"
                )
            return

        try:
            link_path.symlink_to(link_target, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Directory links are unavailable: {error}")

    def remove_directory_link(self, link_path):
        if os.name == "nt":
            link_path.rmdir()
        else:
            link_path.unlink()

    def test_windows_default_targets_the_audited_vault(self):
        with patch.object(MODULE.os, "name", "nt"):
            default_root = MODULE.get_default_root()

        self.assertEqual(
            default_root,
            pathlib.Path(r"G:\Mon Drive\obsidian-vault"),
        )

    def test_new_vault_creates_the_complete_default_directory_tree(self):
        expected_directories = {
            "archive",
            "attachments",
            "notes",
            "notes/books",
            "notes/books/specifications",
            "notes/code",
            "notes/code/bash",
            "notes/code/powershell",
            "notes/code/python",
            "notes/code/sql",
            "notes/devtools",
            "notes/devtools/claude",
            "notes/devtools/codex",
            "notes/devtools/git",
            "notes/devtools/github",
            "notes/devtools/vscode",
            "notes/fintech",
            "notes/hobbies",
            "notes/hobbies/graffiti",
            "notes/hobbies/magic-the-gathering",
            "notes/hobbies/warhammer",
            "notes/inbox",
            "notes/projects",
            "notes/projects/prompts-source-control",
            "notes/work",
            "notes/work/datalog",
            "sandbox",
            "templates",
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory) / "vault"

            self.initialize(root)

            actual_directories = {
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
                if path.is_dir()
            }

        self.assertEqual(actual_directories, expected_directories)

    def test_new_vault_creates_gitkeep_files_in_empty_note_leaves(self):
        expected_gitkeep_files = {
            "notes/books/specifications/.gitkeep",
            "notes/code/bash/.gitkeep",
            "notes/code/powershell/.gitkeep",
            "notes/code/python/.gitkeep",
            "notes/code/sql/.gitkeep",
            "notes/devtools/claude/.gitkeep",
            "notes/devtools/codex/.gitkeep",
            "notes/devtools/git/.gitkeep",
            "notes/devtools/github/.gitkeep",
            "notes/devtools/vscode/.gitkeep",
            "notes/fintech/.gitkeep",
            "notes/hobbies/graffiti/.gitkeep",
            "notes/hobbies/magic-the-gathering/.gitkeep",
            "notes/hobbies/warhammer/.gitkeep",
            "notes/inbox/.gitkeep",
            "notes/projects/prompts-source-control/.gitkeep",
            "notes/work/datalog/.gitkeep",
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory) / "vault"

            self.initialize(root)

            gitkeep_files = sorted(root.rglob(".gitkeep"))
            actual_gitkeep_files = {
                path.relative_to(root).as_posix() for path in gitkeep_files
            }
            gitkeep_contents = [path.read_bytes() for path in gitkeep_files]

        self.assertEqual(actual_gitkeep_files, expected_gitkeep_files)
        self.assertEqual(gitkeep_contents, [b""] * 17)

    def test_custom_empty_note_directory_receives_gitkeep(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory) / "vault"
            empty_directory = root / "notes" / "custom-empty"
            populated_directory = root / "notes" / "custom-populated"
            empty_directory.mkdir(parents=True)
            populated_directory.mkdir()
            note_path = populated_directory / "note.md"
            note_path.write_bytes(b"preserve this note\n")

            self.initialize(root)

            empty_gitkeep_exists = (empty_directory / ".gitkeep").is_file()
            populated_gitkeep_exists = (
                populated_directory / ".gitkeep"
            ).exists()
            note_contents = note_path.read_bytes()

        self.assertTrue(empty_gitkeep_exists)
        self.assertFalse(populated_gitkeep_exists)
        self.assertEqual(note_contents, b"preserve this note\n")

    def test_note_scan_error_is_not_silently_ignored(self):
        scan_error = PermissionError("simulated note scan denial")

        def simulate_walk(_root, *, followlinks, onerror=None):
            self.assertFalse(followlinks)
            if onerror is not None:
                onerror(scan_error)
            return ()

        with tempfile.TemporaryDirectory() as temporary_directory:
            notes_root = pathlib.Path(temporary_directory) / "notes"
            notes_root.mkdir()

            with patch.object(MODULE.os, "walk", side_effect=simulate_walk):
                with self.assertRaisesRegex(PermissionError, "scan denial"):
                    MODULE.find_note_subdirectories(notes_root)

    def test_dry_run_plans_directories_and_gitkeep_files_without_writes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory) / "vault"

            exit_code, stdout, stderr = self.run_main(
                ["--dry-run", "--root", str(root)]
            )

            root_exists = root.exists()

        gitkeep_plan_lines = [
            line
            for line in stdout.splitlines()
            if line.startswith("CREATE  ") and line.endswith(".gitkeep")
        ]
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")
        self.assertFalse(root_exists)
        self.assertEqual(len(gitkeep_plan_lines), 17)
        self.assertIn(
            "Dry-run completed: 29 directories would be created; "
            "0 directories already exist; 17 .gitkeep files would be "
            "created; 0 .gitkeep files already exist.",
            stdout,
        )

    def test_dry_run_matches_the_current_vault_shape(self):
        existing_leaf_directories = (
            "archive",
            "attachments",
            "notes/books/specifications",
            "notes/code/bash",
            "notes/code/powershell",
            "notes/code/python",
            "notes/code/sql",
            "notes/fintech",
            "notes/hobbies/graffiti",
            "notes/hobbies/magic-the-gathering",
            "notes/hobbies/warhammer",
            "notes/inbox",
            "notes/projects/prompts-source-control",
            "notes/work/datalog",
            "sandbox",
            "templates",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory) / "vault"

            for relative_path in existing_leaf_directories:
                (root / relative_path).mkdir(parents=True)

            (root / "notes" / "books" / "book.md").write_bytes(b"book\n")
            specification_path = (
                root / "notes" / "books" / "specifications" / "spec.md"
            )
            specification_path.write_bytes(b"specification\n")
            before_snapshot = self.snapshot(root)

            exit_code, stdout, stderr = self.run_main(
                ["--dry-run", "--root", str(root)]
            )

            after_snapshot = self.snapshot(root)

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")
        self.assertIn(
            "Dry-run completed: 6 directories would be created; "
            "23 directories already exist; 16 .gitkeep files would be "
            "created; 0 .gitkeep files already exist.",
            stdout,
        )
        self.assertEqual(after_snapshot, before_snapshot)

    def test_repeated_runs_are_idempotent_and_report_separate_counts(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory) / "vault"

            first_code, first_stdout, first_stderr = self.run_main(
                ["--root", str(root)]
            )
            first_snapshot = self.snapshot(root)
            second_code, second_stdout, second_stderr = self.run_main(
                ["--root", str(root)]
            )
            second_snapshot = self.snapshot(root)
            third_code, third_stdout, third_stderr = self.run_main(
                ["--root", str(root)]
            )
            third_snapshot = self.snapshot(root)

        self.assertEqual((first_code, second_code, third_code), (0, 0, 0))
        self.assertEqual(
            (first_stderr, second_stderr, third_stderr),
            ("", "", ""),
        )
        self.assertIn(
            "Completed: 29 directories created; 0 directories already "
            "existed; 17 .gitkeep files created; 0 .gitkeep files already "
            "existed.",
            first_stdout,
        )
        repeated_summary = (
            "Completed: 0 directories created; 29 directories already "
            "existed; 0 .gitkeep files created; 17 .gitkeep files already "
            "existed."
        )
        self.assertIn(repeated_summary, second_stdout)
        self.assertIn(repeated_summary, third_stdout)
        self.assertEqual(first_snapshot, second_snapshot)
        self.assertEqual(second_snapshot, third_snapshot)

    def test_system_directories_and_existing_files_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory) / "vault"
            sentinel_paths = []

            for directory_name in (".githooks", ".github", ".obsidian"):
                directory = root / directory_name
                directory.mkdir(parents=True)
                sentinel = directory / "sentinel.bin"
                sentinel.write_bytes(directory_name.encode("utf-8"))
                sentinel_paths.append(sentinel)

            note_path = root / "notes" / "books" / "existing-note.md"
            note_path.parent.mkdir(parents=True)
            note_path.write_bytes(b"existing note\n")
            before_contents = {
                path: path.read_bytes() for path in [*sentinel_paths, note_path]
            }

            self.initialize(root)

            after_contents = {
                path: path.read_bytes() for path in [*sentinel_paths, note_path]
            }
            system_gitkeep_files = [
                path
                for directory_name in (".githooks", ".github", ".obsidian")
                for path in (root / directory_name).rglob(".gitkeep")
            ]

        self.assertEqual(after_contents, before_contents)
        self.assertEqual(system_gitkeep_files, [])

    def test_existing_gitkeep_file_is_counted_without_being_modified(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory) / "vault"
            custom_directory = root / "notes" / "custom"
            custom_directory.mkdir(parents=True)
            gitkeep_path = custom_directory / ".gitkeep"
            gitkeep_path.write_bytes(b"preserve existing content\n")

            result, _output = self.initialize(root)

            gitkeep_contents = gitkeep_path.read_bytes()

        self.assertEqual(gitkeep_contents, b"preserve existing content\n")
        self.assertEqual(result.gitkeep_created, 17)
        self.assertEqual(result.gitkeep_existing, 1)

    def test_gitkeep_directory_conflict_returns_error_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory) / "vault"
            conflict_path = root / "notes" / "custom" / ".gitkeep"
            conflict_path.mkdir(parents=True)
            sentinel_path = conflict_path / "sentinel.bin"
            sentinel_path.write_bytes(b"conflict sentinel\n")

            exit_code, _stdout, stderr = self.run_main(
                ["--root", str(root)]
            )

            conflict_is_directory = conflict_path.is_dir()
            sentinel_contents = sentinel_path.read_bytes()

        self.assertEqual(exit_code, 1)
        self.assertIn("exists but is not a file", stderr)
        self.assertTrue(conflict_is_directory)
        self.assertEqual(sentinel_contents, b"conflict sentinel\n")

    def test_directory_link_is_not_followed_for_gitkeep_creation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = pathlib.Path(temporary_directory)
            root = temporary_root / "vault"
            notes_root = root / "notes"
            notes_root.mkdir(parents=True)
            link_target = temporary_root / "link-target"
            link_target.mkdir()
            link_path = notes_root / "linked-directory"
            self.create_directory_link(link_path, link_target)

            try:
                self.initialize(root)
                target_gitkeep_exists = (link_target / ".gitkeep").exists()
            finally:
                self.remove_directory_link(link_path)

        self.assertFalse(target_gitkeep_exists)

    def test_managed_directory_link_returns_error_without_target_writes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = pathlib.Path(temporary_directory)
            root = temporary_root / "vault"
            root.mkdir()
            link_target = temporary_root / "external-notes"
            link_target.mkdir()
            sentinel_path = link_target / "sentinel.md"
            sentinel_path.write_bytes(b"preserve linked target\n")
            notes_link = root / "notes"
            self.create_directory_link(notes_link, link_target)
            before_snapshot = self.snapshot(link_target)

            try:
                exit_code, _stdout, stderr = self.run_main(
                    ["--root", str(root)]
                )
                after_snapshot = self.snapshot(link_target)
            finally:
                self.remove_directory_link(notes_link)

        self.assertEqual(exit_code, 1)
        self.assertIn("directory link", stderr)
        self.assertEqual(after_snapshot, before_snapshot)


if __name__ == "__main__":
    unittest.main()
