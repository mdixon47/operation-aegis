#!/usr/bin/env bash
set -euo pipefail

announce() {
  echo "==> $1"
}

append_summary() {
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    printf '%s\n' "$1" >> "$GITHUB_STEP_SUMMARY"
  fi
}

RELEASE_ROOT="${RELEASE_ROOT:-dist/staging}"
IMAGE_NAME="${IMAGE_NAME:-project-velocity:staging}"
CONTAINER_NAME="${CONTAINER_NAME:-project-velocity-staging-smoke}"
CONTAINER_PORT="${CONTAINER_PORT:-8000}"
HOST_PORT="${HOST_PORT:-18080}"
BUILD_DOCKER_IMAGE="${BUILD_DOCKER_IMAGE:-auto}"
RUN_CONTAINER_SMOKE_TEST="${RUN_CONTAINER_SMOKE_TEST:-auto}"
VERSION="${GITHUB_SHA:-local}"
DOCKER_STATUS="skipped"

cleanup() {
  if command -v docker >/dev/null 2>&1; then
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

announce "Preparing staging release bundle"
rm -rf "$RELEASE_ROOT"
mkdir -p "$RELEASE_ROOT"

PYTHONPATH=app/src python3 -m project_velocity brief > "$RELEASE_ROOT/project-velocity-brief.txt"
tar -czf "$RELEASE_ROOT/project-velocity-release.tgz" Dockerfile README.md app/src/project_velocity

export RELEASE_ROOT IMAGE_NAME VERSION CONTAINER_PORT DOCKER_STATUS
python3 - <<'PY'
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

release_root = Path(os.environ["RELEASE_ROOT"])
manifest = {
    "application": "project-velocity",
    "version": os.environ["VERSION"],
    "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat(),
    "runtime": {
        "containerImage": os.environ["IMAGE_NAME"],
        "containerPort": int(os.environ["CONTAINER_PORT"]),
        "entrypoint": "python -m project_velocity serve --host 0.0.0.0 --port 8000",
    },
    "artifacts": [
        "project-velocity-brief.txt",
        "project-velocity-release.tgz",
    ],
    "docker": {"status": os.environ["DOCKER_STATUS"]},
}
(release_root / "deployment-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
PY

should_build_docker=false
if command -v docker >/dev/null 2>&1; then
  if [[ "$BUILD_DOCKER_IMAGE" != "false" ]]; then
    should_build_docker=true
  fi
elif [[ "$BUILD_DOCKER_IMAGE" == "true" ]]; then
  echo "BUILD_DOCKER_IMAGE=true but docker is not available." >&2
  exit 1
fi

if [[ "$should_build_docker" == true ]]; then
  announce "Building staging container image $IMAGE_NAME"
  docker build -t "$IMAGE_NAME" .
  DOCKER_STATUS="built"

  if [[ "$RUN_CONTAINER_SMOKE_TEST" != "false" ]]; then
    announce "Running container smoke test on http://127.0.0.1:$HOST_PORT/api/health"
    docker run -d --rm --name "$CONTAINER_NAME" -p "$HOST_PORT:$CONTAINER_PORT" "$IMAGE_NAME" >/dev/null
    export SMOKE_URL="http://127.0.0.1:$HOST_PORT/api/health"
    python3 - <<'PY'
from __future__ import annotations

import json
import os
import time
from urllib.error import URLError
from urllib.request import urlopen

url = os.environ["SMOKE_URL"]
deadline = time.time() + 20
last_error: Exception | None = None

while time.time() < deadline:
    try:
        with urlopen(url, timeout=2) as response:
            payload = json.load(response)
        if payload.get("status") == "ok":
            print(f"Smoke test passed for {url}")
            break
    except (OSError, URLError, TimeoutError, ValueError) as exc:
        last_error = exc
        time.sleep(1)
else:
    raise SystemExit(f"Container smoke test failed for {url}: {last_error}")
PY
    DOCKER_STATUS="built-and-smoke-tested"
  fi
else
  announce "Docker not available; skipping image build and container smoke test."
fi

export RELEASE_ROOT IMAGE_NAME VERSION CONTAINER_PORT DOCKER_STATUS
python3 - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

release_root = Path(os.environ["RELEASE_ROOT"])
manifest_path = release_root / "deployment-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["docker"]["status"] = os.environ["DOCKER_STATUS"]
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
PY

append_summary "### Staging deployment scaffold"
append_summary "- Release bundle: $RELEASE_ROOT/project-velocity-release.tgz"
append_summary "- Manifest: $RELEASE_ROOT/deployment-manifest.json"
append_summary "- Docker status: $DOCKER_STATUS"

announce "Staging scaffold completed; outputs written to $RELEASE_ROOT"
