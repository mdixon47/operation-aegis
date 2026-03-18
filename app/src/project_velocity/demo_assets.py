from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import textwrap


@dataclass(frozen=True)
class DemoExercise:
    name: str
    objective: str
    blocked_by: tuple[str, ...]
    steps: tuple[str, ...]


DEMO_EXERCISES = [
    DemoExercise(
        name="Secret leak drill",
        objective="Demonstrate that leaked cloud credentials are blocked before merge.",
        blocked_by=("Secrets Scan",),
        steps=(
            "Generate the safe demo bundle with `make demo-assets`.",
            "Copy the `repo-overlay` contents onto a throwaway branch.",
            "Open a pull request and verify that the secret scan fails.",
        ),
    ),
    DemoExercise(
        name="SQL injection regression drill",
        objective="Demonstrate that insecure transfer logic is blocked by tests and likely flagged by SAST.",
        blocked_by=("CI Test Gate", "SAST - CodeQL"),
        steps=(
            "Generate the safe demo bundle with `make demo-assets`.",
            "Copy the vulnerable example module and failing test onto a throwaway branch.",
            "Open a pull request and verify that the test gate blocks the merge.",
        ),
    ),
]


def describe_demo_exercises() -> list[dict[str, object]]:
    return [
        {
            "name": exercise.name,
            "objective": exercise.objective,
            "blockedBy": list(exercise.blocked_by),
            "steps": list(exercise.steps),
        }
        for exercise in DEMO_EXERCISES
    ]


def write_demo_bundle(output_dir: Path) -> Path:
    overlay_dir = output_dir / "repo-overlay"
    package_dir = overlay_dir / "app" / "src" / "project_velocity"
    tests_dir = overlay_dir / "app" / "src" / "tests"
    demo_dir = overlay_dir / "demo"
    package_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    demo_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "README.md").write_text(_bundle_readme(), encoding="utf-8")
    (demo_dir / "leaked_credentials.env").write_text(_leaked_credentials_demo(), encoding="utf-8")
    (package_dir / "sql_injection_regression_demo.py").write_text(_sql_injection_demo_module(), encoding="utf-8")
    (tests_dir / "test_sql_injection_regression_demo.py").write_text(_sql_injection_demo_test(), encoding="utf-8")
    return output_dir


def _bundle_readme() -> str:
    return textwrap.dedent(
        """
        # Project Velocity blocked-PR demo bundle

        This bundle is for throwaway branches only. Do not merge these files to main.

        ## How to run the demo

        1. Create a temporary branch from your local checkout.
        2. Copy the `repo-overlay/` contents into the repository root.
        3. Commit the changes and open a pull request.
        4. Observe the expected blocked checks:
           - `Secrets Scan` for `demo/leaked_credentials.env`
           - `CI Test Gate` for `app/src/tests/test_sql_injection_regression_demo.py`
           - `SAST - CodeQL` may also flag the demo SQL file
        5. Close the PR and delete the branch when finished.

        ## Safety notes

        - The credential values are fake and generated for scanning demos only.
        - The SQL injection example is intentionally unsafe and should never be promoted.
        - Keep the generated files out of `main` and production deployment branches.
        """
    ).strip() + "\n"


def _leaked_credentials_demo() -> str:
    access_key = "".join(["AKIA", "QWER", "TYUI", "OPAS", "DFGH"])
    secret_key = "".join(["wJalrXUtn", "FEMI/K7MD", "ENG/bPxR", "fiCYEXAM", "PLEKEY"])
    return f"AWS_ACCESS_KEY_ID={access_key}\nAWS_SECRET_ACCESS_KEY={secret_key}\n"


def _sql_injection_demo_module() -> str:
    return textwrap.dedent(
        """
        def build_balance_lookup_query(account_id: str) -> str:
            return f"SELECT balance FROM accounts WHERE account_id = '{account_id}'"


        def transfer_request_is_safely_parameterized(account_id: str) -> bool:
            query = build_balance_lookup_query(account_id)
            return " OR " not in query.upper()
        """
    ).lstrip()


def _sql_injection_demo_test() -> str:
    payload = "1001001" + "' OR '1'='1"
    return textwrap.dedent(
        f"""
        import unittest

        from project_velocity.sql_injection_regression_demo import transfer_request_is_safely_parameterized


        class SqlInjectionRegressionDemoTests(unittest.TestCase):
            def test_demo_query_builder_blocks_sql_injection(self) -> None:
                self.assertTrue(transfer_request_is_safely_parameterized({payload!r}))


        if __name__ == \"__main__\":
            unittest.main()
        """
    ).lstrip()
