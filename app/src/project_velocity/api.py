from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse

from .demo_assets import describe_demo_exercises
from .quick_transfer import QuickTransferService, TransferRequest, ValidationError
from .risk_brief import BUSINESS_RISKS, INCIDENTS, build_project_velocity_brief

STATIC_DIR = Path(__file__).with_name("static")
REQUIRED_CONTROLS = [
    "CI Test Gate",
    "Secrets Scan",
    "SCA - Dependency Review",
    "SAST - CodeQL",
    "Config Scan",
]


class ProjectVelocityApi:
    def __init__(self, service: QuickTransferService | None = None) -> None:
        self.service = service or QuickTransferService.create_demo_service()

    def dashboard_payload(self) -> dict[str, object]:
        return {
            "program": {
                "name": "Project Velocity",
                "organization": "Skyline Financial Tech",
                "goal": "Ship new banking features every hour without compromising security.",
            },
            "brief": build_project_velocity_brief(),
            "incidents": [asdict(item) for item in INCIDENTS],
            "businessRisks": [asdict(item) for item in BUSINESS_RISKS],
            "requiredChecks": REQUIRED_CONTROLS,
            "accounts": self.service.list_accounts(),
            "recentTransfers": self.service.list_transfers(),
            "demoExercises": describe_demo_exercises(),
        }

    def dispatch(self, method: str, path: str, payload: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
        route = urlparse(path).path
        if method == "GET" and route == "/api/health":
            return HTTPStatus.OK, {"status": "ok", "service": "project-velocity-api"}
        if method == "GET" and route in {"/api/brief", "/api/dashboard"}:
            return HTTPStatus.OK, self.dashboard_payload()
        if method == "GET" and route == "/api/accounts":
            return HTTPStatus.OK, {"accounts": self.service.list_accounts()}
        if method == "GET" and route == "/api/transfers":
            return HTTPStatus.OK, {"recentTransfers": self.service.list_transfers()}
        if method == "POST" and route == "/api/transfers":
            return self._submit_transfer(payload or {})
        return HTTPStatus.NOT_FOUND, {"error": f"No route found for {method} {route}"}

    def _submit_transfer(self, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
        try:
            request = TransferRequest(
                source_account=str(payload["sourceAccount"]),
                destination_account=str(payload["destinationAccount"]),
                amount=Decimal(str(payload["amount"])),
                reference=str(payload["reference"]),
            )
        except (KeyError, ValueError) as exc:
            return HTTPStatus.BAD_REQUEST, {"error": f"Invalid transfer payload: {exc}"}

        try:
            self.service.submit_transfer(request)
        except ValidationError as exc:
            return HTTPStatus.BAD_REQUEST, {"error": str(exc)}

        body = self.dashboard_payload()
        body["message"] = "Transfer processed successfully."
        return HTTPStatus.CREATED, body


class ProjectVelocityHttpServer(HTTPServer):
    def __init__(self, server_address: tuple[str, int], api: ProjectVelocityApi) -> None:
        super().__init__(server_address, ProjectVelocityRequestHandler)
        self.api = api


class ProjectVelocityRequestHandler(BaseHTTPRequestHandler):
    server_version = "ProjectVelocityHTTP/1.0"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/" or path == "/dashboard":
            self._serve_static("index.html")
            return
        if path in {"/dashboard.css", "/dashboard.js"}:
            self._serve_static(path.lstrip("/"))
            return

        status, payload = self.server.api.dispatch("GET", self.path)  # type: ignore[attr-defined]
        self._write_json(status, payload)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "Request body must be valid JSON."})
            return

        status, response = self.server.api.dispatch("POST", self.path, payload)  # type: ignore[attr-defined]
        self._write_json(status, response)

    def _serve_static(self, filename: str) -> None:
        target = (STATIC_DIR / filename).resolve()
        if STATIC_DIR.resolve() not in target.parents and target != STATIC_DIR.resolve():
            self._write_json(HTTPStatus.FORBIDDEN, {"error": "Static path denied."})
            return
        if not target.exists():
            self._write_json(HTTPStatus.NOT_FOUND, {"error": f"Static asset {filename} not found."})
            return

        content_types = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "application/javascript; charset=utf-8"}
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_types.get(target.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ProjectVelocityHttpServer((host, port), ProjectVelocityApi())
    print(f"Project Velocity dashboard available at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Project Velocity server...")
    finally:
        server.server_close()
