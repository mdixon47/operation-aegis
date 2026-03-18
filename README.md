## Skyline Financial Tech - Project Velocity

Project Velocity is a mock banking initiative for Skyline Financial Tech. Its goal is ambitious: ship new banking features every hour instead of every month without sacrificing security, trust, or compliance.

### Scenario

Two recent incidents raised the stakes for Skyline:

- A junior developer accidentally pushed a live AWS secret key into a public repository.
- A critical SQL injection vulnerability was found in the production Quick-Transfer API.

These failures created direct business risk across:

- customer trust
- account data exposure
- financial transaction integrity
- regulatory scrutiny
- deployment shutdown risk

### What this mock project includes

- A secure mock `QuickTransferService` under `app/src/project_velocity/quick_transfer.py`
- A project brief with incidents and business risks under `app/src/project_velocity/risk_brief.py`
- Unit tests that validate transfer integrity and reject SQL-injection-style account input
- GitHub-native DevSecOps workflows that scan, block, test, and report before merge or deployment

### Running the mock project

- `make test` runs the unit test suite
- `make brief` prints the Project Velocity scenario brief
- `make serve` launches the local API and dashboard at `http://127.0.0.1:8000`
- `make demo-assets` generates safe blocked-PR demo files in `/tmp/project-velocity-demo`
- `make docker-build` builds a local container image for the mock app
- `make docker-run` runs the dashboard in Docker on `http://127.0.0.1:8000`
- `make deploy-staging` runs the repository's default staging deployment scaffold

### Container runtime

The repository now includes a lightweight `Dockerfile` for Project Velocity.

- base image: `python:3.11-slim`
- runtime user: non-root `appuser`
- exposed port: `8000`
- default command: `python -m project_velocity serve --host 0.0.0.0 --port 8000`

Dependabot is configured to watch both GitHub Actions and Docker base-image updates.

### API and dashboard

The mock project now includes a small dependency-free HTTP layer and dashboard.

- `GET /api/health` returns a service health response
- `GET /api/dashboard` returns incidents, risks, checks, accounts, transfers, and drill metadata
- `POST /api/transfers` submits a mock quick transfer

The dashboard allows Skyline stakeholders to:

- review the security incidents driving Project Velocity
- inspect protected banking accounts and recent transfers
- simulate a secure quick transfer
- review blocked-PR drill instructions for secrets and SQL injection regressions

### Safe blocked-PR demo assets

`make demo-assets` writes a throwaway demo bundle that is meant for temporary branches only.

The bundle includes:

- a fake leaked-credential file that should trigger `Secrets Scan`
- an intentionally unsafe SQL demo module
- a failing regression test that should trigger `CI Test Gate`

This lets you demonstrate the pipeline blocking unsafe changes without committing live vulnerabilities to `main`.

### Staging deployment scaffold

`Deploy - Staging` now has a repository-local default path even when `DEPLOY_STAGING_COMMAND` is not set.

The scaffold:

- creates a `dist/staging/` release bundle
- writes a deployment manifest and scenario brief snapshot
- builds the Docker image when Docker is available
- runs a container smoke test against `/api/health` when Docker is available
- uploads the generated staging bundle as a workflow artifact

### Release bundle workflow

The repository also includes a `Release Bundle` workflow that builds on the staging scaffold.

- `workflow_dispatch` can package any ref with configurable artifact retention
- pushing a tag like `v1.0.0` packages the repo and publishes a GitHub release automatically
- manual runs can optionally publish a prerelease when `publish_release=true` and `release_tag` is supplied
- the workflow uploads `dist/release/` as an artifact and attaches the bundle files to the release when publishing

### GitHub-native DevSecOps controls

- `CI Test Gate` runs repository tests on pull requests and protected-branch pushes
- `Secrets Scan` blocks commits that introduce leaked credentials
- `SCA - Dependency Review` blocks pull requests that add vulnerable dependencies
- `SAST - CodeQL` analyzes application and workflow code for security issues
- `Config Scan` scans workflow and infrastructure configuration with Trivy
- `Deploy - Staging` re-runs gates before any staging deployment command executes
- `DAST - ZAP Baseline` can scan the staged application after deployment
- `Notify Security` comments on failing PRs and opens or updates tracking issues

### GitHub settings to enable

To enforce merge blocking on `main`, require these checks in branch protection or a ruleset:

- `CI Test Gate`
- `Secrets Scan`
- `SCA - Dependency Review`
- `SAST - CodeQL`
- `Config Scan`

To enforce deployment guarding, create a `staging` environment and optionally add required reviewers.

See `docs/github-ruleset-checklist.md` for a repo-specific checklist covering rulesets, required checks, and staging environment protection.

### Repository variables to configure

- `CI_TEST_COMMAND` - optional override for custom test execution
- `DEPLOY_STAGING_COMMAND` - optional override if you want a custom staging deployment command instead of the repository scaffold
- `STAGING_URL` - required to activate post-deploy DAST with ZAP
