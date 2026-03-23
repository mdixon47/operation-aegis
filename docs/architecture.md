## Project Velocity architecture

Project Velocity is a mock banking application for Skyline Financial Tech. The repository combines a small Python application, a browser dashboard, safe demo assets, and GitHub-native DevSecOps automation to demonstrate how frequent delivery can coexist with strong security controls.

### Goals

- model a secure quick-transfer banking workflow
- expose a simple local API and dashboard for demos
- provide safe drill assets that show how insecure changes would be blocked
- validate changes through CI/CD and pre-deployment security gates

### High-level architecture

The project is organized into four layers:

1. **Application runtime**
   - Python CLI entrypoint in `app/src/project_velocity/__main__.py`
   - HTTP server and request routing in `app/src/project_velocity/api.py`
   - transfer domain logic in `app/src/project_velocity/quick_transfer.py`

2. **Presentation layer**
   - static dashboard assets in `app/src/project_velocity/static/`
   - browser UI backed by JSON endpoints such as `/api/health` and `/api/dashboard`

3. **Demo and documentation layer**
   - scenario brief and business-risk narrative in `app/src/project_velocity/risk_brief.py`
   - blocked-PR demo bundle generation in `app/src/project_velocity/demo_assets.py`
   - operational and workflow documentation under `docs/`

4. **Delivery and security automation**
   - local commands in `Makefile`
   - container runtime in `Dockerfile`
   - GitHub Actions workflows in `.github/workflows/`
   - staging scaffold in `.github/scripts/deploy-staging.sh`

### Runtime components

#### CLI entrypoint

`python -m project_velocity` is the primary entrypoint.

It supports three modes:

- `brief` - prints the Project Velocity scenario brief
- `serve` - starts the local HTTP API and dashboard
- `demo-assets` - writes a safe blocked-PR demo bundle to disk

#### HTTP and API layer

`app/src/project_velocity/api.py` implements a dependency-light server using `HTTPServer` and `BaseHTTPRequestHandler`.

Key endpoints:

- `GET /` and `GET /dashboard` serve the dashboard HTML
- `GET /api/health` returns service status
- `GET /api/dashboard` returns the combined dashboard payload
- `GET /api/accounts` returns seeded account data
- `GET /api/transfers` returns recent transfers
- `POST /api/transfers` validates and processes a mock transfer

The request handler separates static asset serving from JSON API dispatch, which keeps the runtime simple while still supporting both browser and API use cases.

#### Domain and data layer

`QuickTransferService` is the core business component.

It uses an in-memory SQLite database for demo-safe state and provides:

- account initialization and demo seeding
- transfer validation and processing
- account and transfer listing for the dashboard
- defensive normalization of account IDs, amounts, and references

This design keeps state local to the running process and avoids external service dependencies.

#### Dashboard layer

The dashboard is a static front end served directly by the Python process.

- `index.html` defines the layout
- `dashboard.js` fetches `/api/dashboard` and renders incidents, risks, checks, accounts, transfers, and drills
- CSS provides the presentation layer without requiring a front-end build step

### Request and data flow

#### Browser flow

1. A user opens `/` or `/dashboard`.
2. The Python server returns the static dashboard page.
3. The browser loads `dashboard.js`.
4. The script requests `/api/dashboard`.
5. `ProjectVelocityApi` assembles program metadata, incidents, risks, required checks, accounts, transfers, and demo exercises.
6. The browser renders the full operational dashboard.

#### Transfer flow

1. A client submits `POST /api/transfers`.
2. The handler parses the JSON body.
3. `ProjectVelocityApi` builds a `TransferRequest`.
4. `QuickTransferService` validates account IDs, amount, account existence, and balance sufficiency.
5. SQLite state is updated transactionally.
6. The API returns an updated dashboard payload with a success message.

### Local development and runtime packaging

The `Makefile` provides the main developer entrypoints:

- `make test`
- `make brief`
- `make serve`
- `make demo-assets`
- `make docker-build`
- `make docker-run`
- `make deploy-staging`

The `Dockerfile` packages the app as a lightweight container:

- base image: `python:3.11-slim`
- runtime user: non-root `appuser`
- app root: `/app`
- exposed port: `8000`
- default command: `python -m project_velocity serve --host 0.0.0.0 --port 8000`

### Deployment architecture

The repository includes a default staging deployment scaffold in `.github/scripts/deploy-staging.sh`.

That script:

- creates `dist/staging/`
- writes a scenario brief snapshot
- packages a release bundle archive
- generates a deployment manifest
- builds the Docker image when Docker is available
- runs a container smoke test against `/api/health`

This makes the deployment path reproducible even when no custom staging command is configured.

### Security architecture

Project Velocity treats security as part of the delivery architecture rather than a separate afterthought.

Application-side controls include:

- strict transfer input validation
- rejection of malformed account identifiers
- use of parameterized SQL statements
- separation of intentionally unsafe demo content from production paths

Pipeline-side controls include:

- CI test execution before merge
- secret scanning with Gitleaks
- dependency review for pull requests
- CodeQL static analysis
- Trivy configuration scanning
- pre-deployment security gates in the staging workflow

### Architectural constraints and trade-offs

- the app is intentionally dependency-light for portability and demos
- data is ephemeral because the demo service uses in-memory SQLite
- the HTTP server is single-process and not intended for production scale
- static assets are served directly by the backend to avoid a separate front-end toolchain
- demo assets are designed for throwaway branches, not for long-lived environments

### Summary

Project Velocity is a compact full-stack demonstration of secure software delivery. Its architecture emphasizes simplicity: a small Python runtime, a static browser dashboard, local container packaging, and repository-native automation that tests, scans, and gates delivery before deployment.