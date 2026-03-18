#!/usr/bin/env bash
set -euo pipefail

announce() {
  echo "==> $1"
}

if [[ -n "${CI_TEST_COMMAND:-}" ]]; then
  announce "Running repository-defined test command"
  bash -lc "$CI_TEST_COMMAND"
  exit 0
fi

ran_any=false

if [[ -f Makefile ]] && grep -Eq '^test:' Makefile; then
  announce "Running make test"
  make test
  ran_any=true
fi

if [[ -f pnpm-lock.yaml ]]; then
  announce "Running pnpm tests"
  corepack enable
  pnpm install --frozen-lockfile
  pnpm test --if-present
  ran_any=true
elif [[ -f yarn.lock ]]; then
  announce "Running yarn tests"
  corepack enable
  yarn install --immutable || yarn install --frozen-lockfile
  yarn test
  ran_any=true
elif [[ -f package-lock.json || -f package.json ]]; then
  announce "Running npm tests"
  if [[ -f package-lock.json ]]; then
    npm ci
  else
    npm install
  fi
  npm test --if-present
  ran_any=true
fi

if [[ -f requirements.txt || -f requirements-dev.txt || -f pyproject.toml || -d tests || -f pytest.ini ]]; then
  announce "Running python tests"
  python3 -m pip install --upgrade pip
  [[ -f requirements.txt ]] && python3 -m pip install -r requirements.txt
  [[ -f requirements-dev.txt ]] && python3 -m pip install -r requirements-dev.txt
  if ! python3 -c 'import pytest' >/dev/null 2>&1; then
    python3 -m pip install pytest
  fi
  python3 -m pytest
  ran_any=true
fi

if [[ "$ran_any" == false ]]; then
  announce "No repository tests detected; passing without execution"
  echo "Set the CI_TEST_COMMAND repository variable if your project needs a custom test command." >> "$GITHUB_STEP_SUMMARY"
fi
