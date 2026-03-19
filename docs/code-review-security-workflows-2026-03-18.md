## Code review: security and deployment workflows

Date: 2026-03-18

### Scope reviewed

- `.github/workflows/config-scan.yml`
- `.github/workflows/sca-dependency.yml`
- `.github/workflows/deploy-staging.yml`
- `.github/workflows/secrets-scan.yml`
- `.github/scripts/deploy-staging.sh`
- `docs/retrigger-security-workflows.md`

### Errors found and status

1. **Secrets Scan missing pull-request permission**
   - File: `.github/workflows/secrets-scan.yml`
   - Problem: the workflow did not declare `pull-requests: read`, which is the expected permission for the configured PR-triggered Gitleaks usage.
   - Fix: added `pull-requests: read` under `permissions`.
   - Status: corrected in commit `a141256`.

2. **Deploy - Staging could fail on missing `trivy-config.sarif`**
   - File: `.github/workflows/deploy-staging.yml`
   - Problem: SARIF upload could run even when the scan artifact was not created, producing `Path does not exist: trivy-config.sarif`.
   - Fix: switched the scan to the Trivy container path and guarded upload with `hashFiles('trivy-config.sarif') != ''`.
   - Status: corrected in commit `c7f1e88`.

3. **Staging smoke test assumed host port `18080` was always free**
   - File: `.github/scripts/deploy-staging.sh`
   - Problem: local or runner port collisions caused the staging scaffold to fail before the app smoke test could run.
   - Fix: added automatic host-port selection fallback while preserving explicit `HOST_PORT` behavior.
   - Status: corrected in commit `a7d10ba`.

### Validation performed

- Latest `Deploy - Staging` run on `c7f1e88`: **success**
- Latest `Secrets Scan` run on `a141256`: **success**
- Workflow YAML parse checks: passed
- `actionlint` on the workflow set: passed
- `bash -n ./.github/scripts/deploy-staging.sh`: passed
- `python3 -m compileall app/src`: passed

### Notes

- IDE warnings about `vars[...]` and the `staging` environment name are schema/context warnings, not confirmed runtime failures.
- No additional correctness defects were confirmed in the reviewed scope after the fixes above.