from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import sqlite3


class ValidationError(ValueError):
    """Raised when a transfer request violates business or security rules."""


@dataclass(frozen=True)
class TransferRequest:
    source_account: str
    destination_account: str
    amount: Decimal
    reference: str


class QuickTransferService:
    """Secure mock implementation of Skyline's quick-transfer flow."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def initialize(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                owner_name TEXT NOT NULL,
                balance TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS transfers (
                transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_account TEXT NOT NULL,
                destination_account TEXT NOT NULL,
                amount TEXT NOT NULL,
                reference TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        self.connection.commit()

    def seed_demo_data(self) -> None:
        demo_accounts = [
            ("1001001", "Avery Stone", "2500.00"),
            ("2002002", "Jordan Miles", "1250.00"),
            ("3003003", "Skyline Reserve", "50000.00"),
        ]
        self.connection.executemany(
            "INSERT OR REPLACE INTO accounts (account_id, owner_name, balance) VALUES (?, ?, ?)",
            demo_accounts,
        )
        self.connection.commit()

    def submit_transfer(self, request: TransferRequest) -> None:
        source = self._normalize_account_id(request.source_account)
        destination = self._normalize_account_id(request.destination_account)
        amount = self._normalize_amount(request.amount)
        reference = self._normalize_reference(request.reference)

        if source == destination:
            raise ValidationError("Source and destination accounts must differ.")

        source_balance = self._load_balance(source)
        destination_balance = self._load_balance(destination)
        if source_balance is None or destination_balance is None:
            raise ValidationError(
                "Both accounts must exist before a transfer can be processed."
            )
        if source_balance < amount:
            raise ValidationError("Insufficient funds for the requested transfer.")

        with self.connection:
            self.connection.execute(
                "UPDATE accounts SET balance = ? WHERE account_id = ?",
                (self._format_money(source_balance - amount), source),
            )
            self.connection.execute(
                "UPDATE accounts SET balance = ? WHERE account_id = ?",
                (self._format_money(destination_balance + amount), destination),
            )
            self.connection.execute(
                "INSERT INTO transfers (source_account, destination_account, amount, reference) VALUES (?, ?, ?, ?)",
                (source, destination, self._format_money(amount), reference),
            )

    def get_balance(self, account_id: str) -> Decimal:
        normalized = self._normalize_account_id(account_id)
        balance = self._load_balance(normalized)
        if balance is None:
            raise ValidationError("Account does not exist.")
        return balance

    def transfer_count(self) -> int:
        row = self.connection.execute("SELECT COUNT(*) FROM transfers").fetchone()
        return int(row[0])

    def list_accounts(self) -> list[dict[str, str]]:
        rows = self.connection.execute(
            "SELECT account_id, owner_name, balance FROM accounts ORDER BY account_id"
        ).fetchall()
        return [
            {
                "accountId": row[0],
                "ownerName": row[1],
                "balance": self._format_money(Decimal(row[2])),
            }
            for row in rows
        ]

    def list_transfers(self, limit: int = 10) -> list[dict[str, str | int]]:
        rows = self.connection.execute(
            """
            SELECT transfer_id, source_account, destination_account, amount, reference, created_at
            FROM transfers
            ORDER BY transfer_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {
                "transferId": row[0],
                "sourceAccount": row[1],
                "destinationAccount": row[2],
                "amount": self._format_money(Decimal(row[3])),
                "reference": row[4],
                "createdAt": row[5],
            }
            for row in rows
        ]

    def _load_balance(self, account_id: str) -> Decimal | None:
        row = self.connection.execute(
            "SELECT balance FROM accounts WHERE account_id = ?",
            (account_id,),
        ).fetchone()
        return Decimal(row[0]) if row else None

    @staticmethod
    def create_demo_service() -> "QuickTransferService":
        connection = sqlite3.connect(":memory:")
        service = QuickTransferService(connection)
        service.initialize()
        service.seed_demo_data()
        return service

    @staticmethod
    def _normalize_account_id(account_id: str) -> str:
        candidate = account_id.strip()
        if not candidate.isdigit():
            raise ValidationError(
                "Account identifiers must be numeric to prevent malformed queries."
            )
        return candidate

    @staticmethod
    def _normalize_amount(amount: Decimal | str | float) -> Decimal:
        try:
            normalized = Decimal(str(amount)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError) as exc:
            raise ValidationError(
                "Transfer amount must be a valid decimal value."
            ) from exc
        if normalized <= Decimal("0.00"):
            raise ValidationError("Transfer amount must be greater than zero.")
        return normalized

    @staticmethod
    def _normalize_reference(reference: str) -> str:
        cleaned = " ".join(reference.split())
        if not cleaned:
            raise ValidationError("Transfer reference is required.")
        if len(cleaned) > 80:
            raise ValidationError("Transfer reference must stay within 80 characters.")
        return cleaned

    @staticmethod
    def _format_money(amount: Decimal) -> str:
        return str(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
