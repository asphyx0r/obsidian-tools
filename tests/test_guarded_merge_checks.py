"""Verify guarded merge rejection without performing GitHub mutations."""

import copy
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "project_guarded_merge", ROOT / "tools/merge-pull-request.py"
)
MERGE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MERGE
SPEC.loader.exec_module(MERGE)

SHA = "a" * 40
OTHER_SHA = "b" * 40


class GuardedMergeChecksTests(unittest.TestCase):
    def setUp(self):
        self.pull_request = {
            "number": 42,
            "state": "OPEN",
            "isDraft": False,
            "headRefOid": SHA,
            "baseRefName": "main",
            "autoMergeRequest": None,
        }
        self.checks = [
            {
                "name": "Repository audit",
                "state": "SUCCESS",
                "event": "pull_request",
                "workflow": "Repository audit",
            }
        ]
        self.final_state = {
            "data": {
                "repository": {
                    "pullRequest": {
                        "headRefOid": SHA,
                        "baseRefName": "main",
                        "autoMergeRequest": None,
                        "isInMergeQueue": False,
                        "isMergeQueueEnabled": False,
                    }
                }
            }
        }

    def validate(self, checks=None, final_state=None):
        responses = [
            {"data": {"repository": {"autoMergeAllowed": False}}},
            [
                [
                    {
                        "type": "required_status_checks",
                        "parameters": {
                            "required_status_checks": [
                                {"context": "Repository audit", "integration_id": 15368}
                            ]
                        },
                    }
                ]
            ],
            self.pull_request,
            self.checks if checks is None else checks,
            self.final_state if final_state is None else final_state,
        ]
        with patch.object(MERGE, "_run_gh_json", side_effect=responses):
            return MERGE._validate_pull_request(
                "owner/repository",
                "main",
                42,
                expected_head_oid=SHA,
            )

    def test_accepts_successful_pull_request_audit_at_unchanged_head(self):
        self.assertEqual(self.validate()["headRefOid"], SHA)

    def test_rejects_missing_failed_or_pending_required_check(self):
        for checks in (
            [],
            [{**self.checks[0], "state": "FAILURE"}],
            [{**self.checks[0], "state": "PENDING"}],
        ):
            with (
                self.subTest(checks=checks),
                self.assertRaises(MERGE.MergeRequestError),
            ):
                self.validate(checks=checks)

    def test_push_success_cannot_replace_pull_request_validation(self):
        with self.assertRaisesRegex(MERGE.MergeRequestError, "pull_request"):
            self.validate(checks=[{**self.checks[0], "event": "push"}])

    def test_rejects_a_changed_sealed_head(self):
        self.pull_request["headRefOid"] = OTHER_SHA
        with self.assertRaisesRegex(MERGE.MergeRequestError, "head changed"):
            self.validate()

    def test_rejects_a_head_change_during_check_validation(self):
        changed = copy.deepcopy(self.final_state)
        changed["data"]["repository"]["pullRequest"]["headRefOid"] = OTHER_SHA
        with self.assertRaisesRegex(MERGE.MergeRequestError, "head changed"):
            self.validate(final_state=changed)


if __name__ == "__main__":
    unittest.main()
