from decimal import Decimal
import unittest

from project_velocity.api import ProjectVelocityApi


class ProjectVelocityApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api = ProjectVelocityApi()

    def test_dashboard_payload_includes_risks_controls_and_accounts(self) -> None:
        status, payload = self.api.dispatch("GET", "/api/dashboard")

        self.assertEqual(status, 200)
        self.assertEqual(payload["program"]["name"], "Project Velocity")
        self.assertEqual(len(payload["businessRisks"]), 5)
        self.assertGreaterEqual(len(payload["requiredChecks"]), 5)
        self.assertEqual(len(payload["accounts"]), 3)

    def test_post_transfer_updates_dashboard_snapshot(self) -> None:
        status, payload = self.api.dispatch(
            "POST",
            "/api/transfers",
            {
                "sourceAccount": "1001001",
                "destinationAccount": "2002002",
                "amount": Decimal("10.00"),
                "reference": "API smoke transfer",
            },
        )

        self.assertEqual(status, 201)
        self.assertEqual(payload["message"], "Transfer processed successfully.")
        self.assertEqual(payload["accounts"][0]["balance"], "2490.00")
        self.assertEqual(payload["recentTransfers"][0]["reference"], "API smoke transfer")

    def test_post_transfer_rejects_injection_style_payload(self) -> None:
        status, payload = self.api.dispatch(
            "POST",
            "/api/transfers",
            {
                "sourceAccount": "1001001 OR 1=1",
                "destinationAccount": "2002002",
                "amount": "10.00",
                "reference": "Bad request",
            },
        )

        self.assertEqual(status, 400)
        self.assertIn("Account identifiers must be numeric", payload["error"])


if __name__ == "__main__":
    unittest.main()
