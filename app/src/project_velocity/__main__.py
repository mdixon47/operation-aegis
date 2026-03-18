from __future__ import annotations

import argparse
from pathlib import Path

from .api import run_server
from .demo_assets import write_demo_bundle
from .risk_brief import build_project_velocity_brief


def main() -> None:
    parser = argparse.ArgumentParser(description="Project Velocity mock application")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("brief", help="Print the Project Velocity scenario brief")

    serve_parser = subparsers.add_parser("serve", help="Run the mock API and dashboard")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)

    demo_parser = subparsers.add_parser(
        "demo-assets", help="Generate safe blocked-PR demo assets"
    )
    demo_parser.add_argument("--output-dir", default="/tmp/project-velocity-demo")

    args = parser.parse_args()
    command = args.command or "brief"

    if command == "serve":
        run_server(host=args.host, port=args.port)
        return

    if command == "demo-assets":
        output_dir = write_demo_bundle(Path(args.output_dir))
        print(f"Safe demo assets written to {output_dir}")
        return

    print(build_project_velocity_brief())


if __name__ == "__main__":
    main()
