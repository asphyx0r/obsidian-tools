import importlib.util
import io
import os
import pathlib
import stat
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

            attributes = getattr(path.lstat(), "st_file_attributes", 0)
            if path.is_symlink() or attributes & getattr(
                stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0
            ):
                records.append(("link", relative_path, os.readlink(path)))
            elif path.is_dir():
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

    def assert_preflight_failure(self, root, snapshot_root, message):
        before_snapshot = self.snapshot(snapshot_root)
        for dry_run in (True, False):
            with self.subTest(root=root, dry_run=dry_run):
                arguments = ["--root", str(root)]
                if dry_run:
                    arguments.append("--dry-run")
                code, stdout, stderr = self.run_main(arguments)
                self.assertEqual(code, 1)
                self.assertEqual(stdout, "")
                self.assertIn(message, stderr)
                self.assertEqual(self.snapshot(snapshot_root), before_snapshot)

    def test_windows_default_targets_the_audited_vault(self):
        with patch.object(MODULE.os, "name", "nt"):
            default_root = MODULE.get_default_root()

        self.assertEqual(
            default_root,
            pathlib.Path(r"G:\Mon Drive\obsidian-vault"),
        )

    def test_root_option_requires_a_value_instead_of_another_option(self):
        for root_option in ("-r", "--root"):
            for value in (
                "--dry-run", "--help", "--version", "-v", "--unknown", "-name"
            ):
                with self.subTest(root_option=root_option, value=value):
                    with patch.object(MODULE, "initialize_vault") as initialize:
                        code, stdout, stderr = self.run_main(
                            [root_option, value]
                        )
                    self.assertEqual(code, 2)
                    self.assertEqual(stdout, "")
                    self.assertIn("requires a path", stderr)
                    initialize.assert_not_called()

    def test_explicit_root_values_preserve_supported_path_forms(self):
        cases = (
            (["--root=-name"], pathlib.Path("-name")),
            (["--root", "./-name"], pathlib.Path("./-name")),
            (["-r", "vault with spaces"], pathlib.Path("vault with spaces")),
            (["--root", "~/vault"], pathlib.Path.home() / "vault"),
            (["--root", "$OBSIDIAN_TEST_ROOT"], pathlib.Path("expanded vault")),
        )
        with patch.dict(os.environ, {"OBSIDIAN_TEST_ROOT": "expanded vault"}):
            for arguments, expected_root in cases:
                with self.subTest(arguments=arguments):
                    self.assertEqual(
                        MODULE.parse_arguments(["--dry-run", *arguments]),
                        (expected_root, True, False),
                    )

    def test_new_vault_creates_the_complete_default_directory_tree(self):
        expected_directories = {
            "archive",
            "archive/goals",
            "archive/tasks",
            "attachments",
            "attachments/notes",
            "attachments/notes/profiles",
            "attachments/notes/profiles/hinge",
            "notes",
            "notes/ai",
            "notes/ai/chatgpt",
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
            "notes/devtools/github/repositories",
            "notes/devtools/vscode",
            "notes/terminal",
            "notes/terminal/tmux",
            "notes/terminal/psmux",
            "notes/fintech",
            "notes/hobbies",
            "notes/hobbies/graffiti",
            "notes/hobbies/magic-the-gathering",
            "notes/hobbies/warhammer",
            "notes/goals",
            "notes/gtd",
            "notes/inbox",
            "notes/profiles",
            "notes/recipes",
            "notes/projects",
            "notes/projects/prompts-source-control",
            "notes/tasks",
            "notes/tasks/backlogs",
            "notes/tasks/daily",
            "notes/tasks/recurring",
            "notes/work",
            "notes/work/datalog",
            "sandbox",
            "templates",
            "templates/gtd",
            "templates/profiles",
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"

            self.initialize(root)

            actual_directories = {
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
                if path.is_dir()
            }

        self.assertEqual(actual_directories, expected_directories)

    def test_new_vault_creates_gitkeep_files_in_selected_empty_leaves(self):
        expected_gitkeep_files = {
            "attachments/notes/profiles/hinge/.gitkeep",
            "notes/ai/chatgpt/.gitkeep",
            "notes/books/specifications/.gitkeep",
            "notes/code/bash/.gitkeep",
            "notes/code/powershell/.gitkeep",
            "notes/code/python/.gitkeep",
            "notes/code/sql/.gitkeep",
            "notes/devtools/claude/.gitkeep",
            "notes/devtools/codex/.gitkeep",
            "notes/devtools/git/.gitkeep",
            "notes/devtools/github/repositories/.gitkeep",
            "notes/devtools/vscode/.gitkeep",
            "notes/terminal/tmux/.gitkeep",
            "notes/terminal/psmux/.gitkeep",
            "notes/fintech/.gitkeep",
            "notes/goals/.gitkeep",
            "notes/gtd/.gitkeep",
            "notes/hobbies/graffiti/.gitkeep",
            "notes/hobbies/magic-the-gathering/.gitkeep",
            "notes/hobbies/warhammer/.gitkeep",
            "notes/inbox/.gitkeep",
            "notes/profiles/.gitkeep",
            "notes/recipes/.gitkeep",
            "notes/projects/prompts-source-control/.gitkeep",
            "notes/tasks/backlogs/.gitkeep",
            "notes/tasks/daily/.gitkeep",
            "notes/tasks/recurring/.gitkeep",
            "notes/work/datalog/.gitkeep",
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"

            self.initialize(root)

            gitkeep_files = sorted(root.rglob(".gitkeep"))
            actual_gitkeep_files = {
                path.relative_to(root).as_posix() for path in gitkeep_files
            }
            gitkeep_contents = [path.read_bytes() for path in gitkeep_files]

        self.assertEqual(actual_gitkeep_files, expected_gitkeep_files)
        self.assertEqual(gitkeep_contents, [b""] * 28)

    def test_custom_empty_note_directory_receives_gitkeep(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"
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
            notes_root = pathlib.Path(temporary_directory).resolve() / "notes"
            notes_root.mkdir()

            with patch.object(MODULE.os, "walk", side_effect=simulate_walk):
                with self.assertRaisesRegex(PermissionError, "scan denial"):
                    MODULE.find_note_subdirectories(notes_root)

    def test_late_directory_conflict_fails_before_any_creation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"
            root.mkdir()
            (root / "templates").write_bytes(b"preserve template conflict\n")
            self.assert_preflight_failure(root, root, "not a directory")

    def test_file_ancestor_fails_before_any_creation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            base = pathlib.Path(temporary_directory).resolve()
            parent = base / "file-parent"
            parent.write_bytes(b"preserve parent\n")
            self.assert_preflight_failure(parent / "vault", base, "not a directory")

    def test_gitkeep_conflict_fails_before_any_creation(self):
        for relative_path in ("notes/custom", "attachments/notes/profiles/hinge"):
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = pathlib.Path(temporary_directory).resolve() / "vault"
                    conflict = root / relative_path / ".gitkeep"
                    conflict.mkdir(parents=True)
                    (conflict / "sentinel").write_bytes(b"preserve\n")
                    self.assert_preflight_failure(root, root, "not a file")

    def test_note_scan_failure_prevents_all_creations(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"
            (root / "notes").mkdir(parents=True)
            with patch.object(
                MODULE.os, "walk", side_effect=PermissionError("scan denied")
            ):
                self.assert_preflight_failure(root, root, "scan denied")

    def test_denied_creation_access_prevents_all_creations(self):
        for target in ("templates", "notes/custom"):
            with self.subTest(target=target):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = pathlib.Path(temporary_directory).resolve() / "vault"
                    blocked = root / target
                    blocked.mkdir(parents=True)
                    real_access = MODULE.os.access

                    def check_access(path, mode):
                        if pathlib.Path(path) == blocked and mode & os.W_OK:
                            return False
                        return real_access(path, mode)

                    if target == "templates":
                        blocked = root
                    with patch.object(MODULE.os, "access", side_effect=check_access):
                        self.assert_preflight_failure(root, root, "access")

    def test_complete_read_only_vault_needs_no_write_access(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"
            self.initialize(root)
            before = self.snapshot(root)
            real_access = MODULE.os.access

            def check_access(path, mode):
                self.assertFalse(mode & os.W_OK)
                return real_access(path, mode)

            with patch.object(MODULE.os, "access", side_effect=check_access):
                for dry_run in (True, False):
                    result, _output = self.initialize(root, dry_run=dry_run)
                    self.assertEqual(result.directories_created, 0)
                    self.assertEqual(result.gitkeep_created, 0)
            self.assertEqual(self.snapshot(root), before)

    def test_disappearing_filesystem_root_raises_instead_of_looping(self):
        path = pathlib.Path.cwd() / "vault"
        statuses = [None] * len(path.parents)
        statuses.append(AssertionError("filesystem root inspected repeatedly"))
        with patch.object(MODULE, "_read_status", side_effect=statuses):
            with self.assertRaises(FileNotFoundError):
                MODULE._require_creation_access(path)

    def test_ancestor_links_are_rejected_before_any_creation(self):
        for suffix in ("vault", "existing-vault", "../vault"):
            with self.subTest(suffix=suffix):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    base = pathlib.Path(temporary_directory).resolve()
                    target = base / "target"
                    target.mkdir()
                    (target / "existing-vault").mkdir()
                    link = base / "linked-parent"
                    self.create_directory_link(link, target)
                    try:
                        self.assert_preflight_failure(
                            link / suffix, base, "directory link"
                        )
                    finally:
                        self.remove_directory_link(link)

    def test_broken_directory_link_is_rejected_in_dry_run(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            base = pathlib.Path(temporary_directory).resolve()
            target = base / "target"
            target.mkdir()
            link = base / "broken-link"
            self.create_directory_link(link, target)
            target.rmdir()
            try:
                self.assert_preflight_failure(link / "vault", base, "directory link")
            finally:
                self.remove_directory_link(link)

    def test_execution_error_reports_partial_initialization_without_rollback(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"
            real_mkdir = pathlib.Path.mkdir

            def create_directory(path, *args, **kwargs):
                if path == root / "templates":
                    raise PermissionError("simulated write failure")
                return real_mkdir(path, *args, **kwargs)

            with patch.object(pathlib.Path, "mkdir", new=create_directory):
                code, stdout, stderr = self.run_main(["--root", str(root)])

            self.assertEqual(code, 1)
            self.assertIn("simulated write failure", stderr)
            self.assertIn("partial", stderr)
            self.assertNotIn("Completed:", stdout)
            self.assertTrue((root / "notes").is_dir())

    def test_missing_root_ancestors_are_planned_and_created(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            base = pathlib.Path(temporary_directory).resolve()
            root = base / "missing" / "parent" / "vault"
            plan, output = self.initialize(root, dry_run=True)
            self.assertFalse((base / "missing").exists())
            self.assertIn(f"CREATE  {base / 'missing'}\n", output)
            self.assertIn(f"CREATE  {base / 'missing' / 'parent'}\n", output)
            result, _output = self.initialize(root)
            self.assertEqual(result.directories_created, plan.directories_planned)
            self.assertEqual(result.gitkeep_created, plan.gitkeep_planned)
            self.assertTrue(root.is_dir())

    def test_dry_run_plans_directories_and_gitkeep_files_without_writes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"

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
        self.assertEqual(len(gitkeep_plan_lines), 28)
        self.assertIn(
            "Dry-run completed: 50 directories would be created; "
            "0 directories already exist; 28 .gitkeep files would be "
            "created; 0 .gitkeep files already exist.",
            stdout,
        )

    def test_dry_run_on_a_partially_populated_vault_preserves_all_entries(self):
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
            root = pathlib.Path(temporary_directory).resolve() / "vault"

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
            "Dry-run completed: 27 directories would be created; "
            "23 directories already exist; 27 .gitkeep files would be "
            "created; 0 .gitkeep files already exist.",
            stdout,
        )
        self.assertEqual(after_snapshot, before_snapshot)

    def test_repeated_runs_are_idempotent_and_report_separate_counts(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"

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
            "Completed: 50 directories created; 0 directories already "
            "existed; 28 .gitkeep files created; 0 .gitkeep files already "
            "existed.",
            first_stdout,
        )
        repeated_summary = (
            "Completed: 0 directories created; 50 directories already "
            "existed; 0 .gitkeep files created; 28 .gitkeep files already "
            "existed."
        )
        self.assertIn(repeated_summary, second_stdout)
        self.assertIn(repeated_summary, third_stdout)
        self.assertEqual(first_snapshot, second_snapshot)
        self.assertEqual(second_snapshot, third_snapshot)

    def test_system_directories_and_existing_files_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory).resolve() / "vault"
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

    def test_hinge_gitkeep_plan_matches_execution(self):
        cases = (
            (None, None, True),
            ("profile.png", b"preserve attachment\n", False),
            (".gitkeep", b"preserve existing gitkeep\n", False),
        )

        for filename, content, should_create in cases:
            with self.subTest(filename=filename):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = pathlib.Path(temporary_directory).resolve() / "vault"
                    hinge = (
                        root / "attachments" / "notes" / "profiles" / "hinge"
                    )
                    hinge.mkdir(parents=True)
                    unrelated = root / "attachments" / "custom-empty"
                    unrelated.mkdir()
                    if filename is not None:
                        (hinge / filename).write_bytes(content)
                    before_snapshot = self.snapshot(root)

                    exit_code, stdout, stderr = self.run_main(
                        ["--dry-run", "--root", str(root)]
                    )

                    self.assertEqual(exit_code, 0)
                    self.assertEqual(stderr, "")
                    self.assertEqual(self.snapshot(root), before_snapshot)
                    plan_line = f"CREATE  {hinge / '.gitkeep'}"
                    self.assertEqual(
                        plan_line in stdout.splitlines(), should_create
                    )

                    self.initialize(root)

                    if should_create:
                        self.assertEqual(
                            (hinge / ".gitkeep").read_bytes(), b""
                        )
                    elif filename == "profile.png":
                        self.assertFalse((hinge / ".gitkeep").exists())
                    if filename is not None:
                        self.assertEqual(
                            (hinge / filename).read_bytes(), content
                        )
                    self.assertFalse((unrelated / ".gitkeep").exists())
                    for parent in (hinge.parent, hinge.parent.parent):
                        self.assertFalse((parent / ".gitkeep").exists())

    def test_existing_gitkeep_file_is_counted_without_being_modified(self):
        cases = (
            ("notes/custom", 28),
            ("notes/devtools/github", 28),
            ("attachments/notes/profiles/hinge", 27),
        )

        for relative_path, expected_created in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = pathlib.Path(temporary_directory).resolve() / "vault"
                    directory = root / relative_path
                    directory.mkdir(parents=True)
                    gitkeep_path = directory / ".gitkeep"
                    gitkeep_path.write_bytes(b"preserve existing content\n")

                    result, _output = self.initialize(root)

                    gitkeep_contents = gitkeep_path.read_bytes()

                self.assertEqual(
                    gitkeep_contents, b"preserve existing content\n"
                )
                self.assertEqual(result.gitkeep_created, expected_created)
                self.assertEqual(result.gitkeep_existing, 1)

    def test_gitkeep_directory_conflict_returns_error_without_overwrite(self):
        relative_paths = (
            "notes/custom",
            "attachments/notes/profiles/hinge",
        )
        for relative_path in relative_paths:
            for dry_run in (False, True):
                with self.subTest(
                    relative_path=relative_path, dry_run=dry_run
                ):
                    with tempfile.TemporaryDirectory() as temporary_directory:
                        root = pathlib.Path(temporary_directory).resolve() / "vault"
                        conflict_path = root / relative_path / ".gitkeep"
                        conflict_path.mkdir(parents=True)
                        sentinel_path = conflict_path / "sentinel.bin"
                        sentinel_path.write_bytes(b"conflict sentinel\n")
                        before_snapshot = self.snapshot(root)
                        arguments = ["--root", str(root)]
                        if dry_run:
                            arguments.append("--dry-run")

                        exit_code, _stdout, stderr = self.run_main(arguments)

                        self.assertEqual(exit_code, 1)
                        self.assertIn("exists but is not a file", stderr)
                        self.assertTrue(conflict_path.is_dir())
                        self.assertEqual(
                            sentinel_path.read_bytes(), b"conflict sentinel\n"
                        )
                        if dry_run:
                            self.assertEqual(
                                self.snapshot(root), before_snapshot
                            )

    def test_directory_link_is_not_followed_for_gitkeep_creation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = pathlib.Path(temporary_directory).resolve()
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
        relative_paths = (
            "",
            "notes",
            "notes/devtools/github/repositories",
            "notes/profiles",
            "attachments/notes",
            "attachments/notes/profiles",
            "attachments/notes/profiles/hinge",
        )

        for relative_path in relative_paths:
            for dry_run in (False, True):
                with self.subTest(
                    relative_path=relative_path, dry_run=dry_run
                ):
                    with tempfile.TemporaryDirectory() as temporary_directory:
                        temporary_root = pathlib.Path(temporary_directory).resolve()
                        root = temporary_root / "vault"
                        link_target = temporary_root / "external-directory"
                        link_target.mkdir()
                        sentinel_path = link_target / "sentinel.md"
                        sentinel_path.write_bytes(b"preserve linked target\n")
                        directory_link = root / relative_path
                        directory_link.parent.mkdir(parents=True, exist_ok=True)
                        self.create_directory_link(directory_link, link_target)
                        before_snapshot = self.snapshot(link_target)
                        before_vault_snapshot = self.snapshot(temporary_root)
                        arguments = ["--root", str(root)]
                        if dry_run:
                            arguments.append("--dry-run")

                        try:
                            exit_code, stdout, stderr = self.run_main(
                                arguments
                            )
                            after_snapshot = self.snapshot(link_target)
                            after_vault_snapshot = self.snapshot(temporary_root)
                        finally:
                            self.remove_directory_link(directory_link)

                    self.assertEqual(exit_code, 1)
                    self.assertEqual(stdout, "")
                    self.assertIn("directory link", stderr)
                    self.assertEqual(after_snapshot, before_snapshot)
                    self.assertEqual(after_vault_snapshot, before_vault_snapshot)


if __name__ == "__main__":
    unittest.main()
