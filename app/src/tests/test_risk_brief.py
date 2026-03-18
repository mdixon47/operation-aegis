import unittest

from project_velocity.risk_brief import BUSINESS_RISKS, INCIDENTS, build_project_velocity_brief


class ProjectVelocityBriefTests(unittest.TestCase):
    def test_brief_contains_the_two_key_incidents(self) -> None:
        brief = build_project_velocity_brief()

        self.assertEqual(len(INCIDENTS), 2)
        self.assertIn("Public AWS credential exposure", brief)
        self.assertIn("Quick-Transfer SQL injection", brief)

    def test_brief_lists_all_business_risks(self) -> None:
        brief = build_project_velocity_brief()

        self.assertEqual(len(BUSINESS_RISKS), 5)
        for risk in BUSINESS_RISKS:
            self.assertIn(risk.name, brief)


if __name__ == "__main__":
    unittest.main()
