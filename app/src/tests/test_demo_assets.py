from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from project_velocity.demo_assets import write_demo_bundle


class DemoAssetsTests(unittest.TestCase):
    def test_demo_bundle_writes_expected_overlay_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            output_dir = write_demo_bundle(Path(temp_dir))

            bundle_readme = (output_dir / "README.md").read_text(encoding="utf-8")
            leak_file = (output_dir / "repo-overlay" / "demo" / "leaked_credentials.env").read_text(encoding="utf-8")
            regression_test = (output_dir / "repo-overlay" / "app" / "src" / "tests" / "test_sql_injection_regression_demo.py").read_text(encoding="utf-8")

            self.assertIn("throwaway branches only", bundle_readme)
            self.assertIn("AWS_ACCESS_KEY_ID=AKIA", leak_file)
            self.assertIn("test_demo_query_builder_blocks_sql_injection", regression_test)


if __name__ == "__main__":
    unittest.main()
