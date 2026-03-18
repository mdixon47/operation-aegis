from decimal import Decimal
import sqlite3
import unittest

from project_velocity.quick_transfer import (
    QuickTransferService,
    TransferRequest,
    ValidationError,
)


class QuickTransferServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.service = QuickTransferService(self.connection)
        self.service.initialize()
        self.service.seed_demo_data()

    def tearDown(self) -> None:
        self.connection.close()

    def test_successful_transfer_updates_balances_and_ledger(self) -> None:
        request = TransferRequest(
            source_account="1001001",
            destination_account="2002002",
            amount=Decimal("125.50"),
            reference="Payroll advance",
        )

        self.service.submit_transfer(request)

        self.assertEqual(self.service.get_balance("1001001"), Decimal("2374.50"))
        self.assertEqual(self.service.get_balance("2002002"), Decimal("1375.50"))
        self.assertEqual(self.service.transfer_count(), 1)

    def test_sql_injection_style_account_identifier_is_rejected(self) -> None:
        request = TransferRequest(
            source_account="1001001 OR 1=1",
            destination_account="2002002",
            amount=Decimal("10.00"),
            reference="Injection probe",
        )

        with self.assertRaises(ValidationError):
            self.service.submit_transfer(request)

        self.assertEqual(self.service.transfer_count(), 0)
        self.assertEqual(self.service.get_balance("1001001"), Decimal("2500.00"))

    def test_transfer_with_insufficient_funds_is_blocked(self) -> None:
        request = TransferRequest(
            source_account="2002002",
            destination_account="3003003",
            amount=Decimal("5000.00"),
            reference="Out-of-policy attempt",
        )

        with self.assertRaises(ValidationError):
            self.service.submit_transfer(request)

        self.assertEqual(self.service.transfer_count(), 0)

    def test_list_views_return_dashboard_friendly_shapes(self) -> None:
        self.service.submit_transfer(
            TransferRequest(
                source_account="1001001",
                destination_account="2002002",
                amount=Decimal("15.00"),
                reference="Dashboard refresh",
            )
        )

        accounts = self.service.list_accounts()
        transfers = self.service.list_transfers()

        self.assertEqual(accounts[0]["accountId"], "1001001")
        self.assertEqual(accounts[0]["ownerName"], "Avery Stone")
        self.assertEqual(transfers[0]["reference"], "Dashboard refresh")
        self.assertIn("createdAt", transfers[0])


if __name__ == "__main__":
    unittest.main()
