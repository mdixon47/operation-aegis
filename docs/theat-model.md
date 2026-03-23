## Project Velocity threat model

This document gives a brief threat model for Project Velocity and summarizes the working solution currently implemented in the repository.

### System context

Project Velocity is a mock banking application for Skyline Financial Tech. It exposes a small HTTP API and dashboard, supports a quick-transfer workflow, and is protected by repository-native CI/CD security controls.

### Key assets

- transfer integrity
- account and transaction data
- deployment pipeline trust
- repository secrets and credentials
- confidence in staged releases

### Primary threats

#### Credential leakage

Accidental commits of cloud or service credentials could expose infrastructure and trigger incident response.

#### Injection and unsafe input handling

Malformed account IDs or unsafe query patterns could lead to SQL injection or data tampering.

#### Vulnerable or risky code changes

Changes that weaken validation, introduce insecure dependencies, or bypass expected checks could make the application unsafe to release.

#### Unsafe deployment path

Shipping to staging without re-running tests and security gates could allow regressions to move downstream.

### Working solution

The current repository addresses those threats with a combination of application controls and pipeline controls.

#### Application controls

- `QuickTransferService` validates account IDs, amounts, and transfer references
- account identifiers must be numeric, reducing malformed-input risk
- SQL updates use parameterized statements instead of string-built queries
- the demo runtime uses in-memory SQLite to avoid external infrastructure dependencies
- intentionally unsafe examples are isolated to generated demo assets for throwaway branches

#### Delivery and security controls

- `CI Test Gate` validates the repository before merge
- `Secrets Scan` uses Gitleaks to detect leaked credentials
- `SCA - Dependency Review` checks pull requests for risky dependency changes
- `SAST - CodeQL` analyzes code for security defects
- `Config Scan` uses Trivy to scan workflow and configuration files
- `Deploy - Staging` re-runs gates before the staging deployment path proceeds
- the staging scaffold performs a container health check against `/api/health`

### Expected outcome

The working solution is designed to stop common high-impact failures early:

- leaked secrets should be blocked before merge
- insecure transfer regressions should be caught by tests and analysis
- misconfigured or risky changes should be surfaced by security workflows
- staging deployments should only proceed after gates pass

### Residual risk

This is still a demo-oriented system, so some trade-offs remain:

- the HTTP server is lightweight and not production-scaled
- data is ephemeral because the demo service uses in-memory storage
- security assurance depends in part on repository settings such as required checks and environment protections

### Summary

Project Velocity’s threat model is centered on protecting secrets, transfer integrity, and release trust. The working solution combines secure application behavior with CI/CD guardrails so that risky changes are detected before merge or deployment.