"""Protect project CI coverage and coherent quality dependency updates."""

import copy
import fnmatch
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "project_workflow_contracts", ROOT / "tools/repository-audit/workflow-contracts.py"
)
CONTRACTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACTS)


class QualityDependencyTests(unittest.TestCase):
    def test_declared_gate_rejects_partial_updates_on_each_platform(self):
        config = json.loads((ROOT / ".starter-kit-project.json").read_text())
        config["checks"] = [
            check
            for check in config["checks"]
            if "tools/quality/check-versions.py" in check["argv"]
        ]
        for platform in ("linux", "windows"):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as temp:
                fixture = Path(temp)
                quality = fixture / "tools/quality"
                quality.mkdir(parents=True)
                for source in (ROOT / "tools/quality").iterdir():
                    if source.is_file():
                        shutil.copy2(source, quality / source.name)
                (fixture / ".starter-kit-project.json").write_text(json.dumps(config))
                argv = [
                    sys.executable,
                    "-B",
                    "-c",
                    "import sys; from pathlib import Path; "
                    "sys.path.insert(0, sys.argv[1]); "
                    "from project_validation import run_checks; "
                    "sys.exit(run_checks(Path(sys.argv[2]), platform=sys.argv[3]))",
                    str(ROOT / "tools"),
                    str(fixture),
                    platform,
                ]
                clean = subprocess.run(argv, capture_output=True, text=True, timeout=30)
                self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
                registry_path = quality / "versions.json"
                registry = json.loads(registry_path.read_text())
                registry["python"]["ruff"] = "0.0.0"
                registry_path.write_text(json.dumps(registry))
                drift = subprocess.run(argv, capture_output=True, text=True, timeout=30)
                self.assertNotEqual(drift.returncode, 0, drift.stdout + drift.stderr)
                self.assertIn("requirements.in", drift.stdout + drift.stderr)
                self.assertIn("requirements.lock", drift.stdout + drift.stderr)


class ProjectWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.workflow = CONTRACTS.load_workflow(
            ROOT / ".github/workflows/repository-audit.yml"
        )
        self.registry = json.loads((ROOT / "tools/quality/versions.json").read_text())

    def test_push_filters_cover_feature_dependency_and_release_branches(self):
        filters = self.workflow["on"]["push"]["branches"]
        for branch in (
            "main",
            "master",
            "codex/ci-release-alignment",
            "feat/new-command",
            "dependabot/pip/tools/quality/ruff-0.16.8",
            "release/2.5.1",
            "codex/release-preflight-2.5.1",
        ):
            with self.subTest(branch=branch):
                self.assertTrue(
                    any(fnmatch.fnmatchcase(branch, item) for item in filters)
                )

    def test_contract_accepts_all_branch_validation(self):
        self.workflow["on"]["push"]["branches"] = ["**"]
        CONTRACTS.validate_workflow("repository-audit", self.workflow, self.registry)

    def test_contract_rejects_weakened_validation_boundaries(self):
        variants = []
        changed = copy.deepcopy(self.workflow)
        changed["permissions"]["contents"] = "write"
        variants.append(changed)
        changed = copy.deepcopy(self.workflow)
        changed["on"]["push"]["branches"] = ["main"]
        variants.append(changed)
        changed = copy.deepcopy(self.workflow)
        del changed["on"]["release"]
        variants.append(changed)
        changed = copy.deepcopy(self.workflow)
        del changed["on"]["push"]["tags"]
        variants.append(changed)
        for index, changed in enumerate(variants):
            with (
                self.subTest(variant=index),
                self.assertRaises(CONTRACTS.ContractError),
            ):
                CONTRACTS.validate_workflow("repository-audit", changed, self.registry)


if __name__ == "__main__":
    unittest.main()
